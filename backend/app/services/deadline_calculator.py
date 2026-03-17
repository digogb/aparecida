"""
Deadline calculator — computes due dates in Brazilian business days,
skipping weekends and holidays from the database.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Holiday
from app.models.task import Task

logger = logging.getLogger(__name__)


async def _load_holidays(db: AsyncSession) -> set[date]:
    """Load all holiday dates from the database."""
    result = await db.execute(select(Holiday.date))
    return set(result.scalars().all())


async def calculate_due_date(
    start: date,
    business_days: int,
    db: AsyncSession,
) -> date:
    """
    Return the date that is `business_days` working days after `start`,
    skipping weekends (Sat/Sun) and holidays from the database.
    """
    holidays = await _load_holidays(db)

    current = start
    remaining = business_days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            remaining -= 1

    return current


async def update_all_deadlines(db: AsyncSession) -> int:
    """
    Recalculate due_date for all tasks whose due_date is None
    and that have a source_ref with a 'business_days' key.

    Returns count of tasks updated.
    """
    from datetime import datetime, timezone

    holidays = await _load_holidays(db)

    result = await db.execute(
        select(Task).where(
            Task.due_date.is_(None),
            Task.source_ref.is_not(None),
        )
    )
    tasks = list(result.scalars().all())

    updated = 0
    for task in tasks:
        ref = task.source_ref or {}
        business_days = ref.get("business_days")
        if business_days is None:
            continue

        start = task.created_at.date()
        current = start
        remaining = int(business_days)
        while remaining > 0:
            current += timedelta(days=1)
            if current.weekday() < 5 and current not in holidays:
                remaining -= 1

        task.due_date = datetime(current.year, current.month, current.day, tzinfo=timezone.utc)
        updated += 1

    if updated:
        await db.commit()
        logger.info("Updated deadlines for %d tasks", updated)

    return updated
