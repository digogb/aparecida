import { describe, expect, it } from 'vitest'
import { fetchDefaultBoard, createTask, moveTask } from './taskApi'

describe('fetchDefaultBoard', () => {
  it('retorna board com colunas', async () => {
    const board = await fetchDefaultBoard()

    expect(board.id).toBe('board-1')
    expect(board.columns).toHaveLength(1)
    expect(board.columns[0].tasks).toHaveLength(1)
  })
})

describe('createTask', () => {
  it('retorna tarefa criada com id gerado', async () => {
    const task = await createTask({
      column_id: 'col-todo',
      title: 'Nova tarefa',
      priority: 'medium',
    })

    expect(task.id).toBe('task-new')
    expect(task.title).toBe('Nova tarefa')
    expect(task.column_id).toBe('col-todo')
  })
})

describe('moveTask', () => {
  it('retorna tarefa com nova coluna e posição', async () => {
    const task = await moveTask('task-1', { column_id: 'col-done', position: 0 })

    expect(task.column_id).toBe('col-done')
  })
})
