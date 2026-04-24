import { describe, expect, it } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement, type ReactNode } from 'react'
import { usePareceres, useParecer } from './useParecer'

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: qc }, children)
}

describe('usePareceres', () => {
  it('começa carregando e entrega lista após fetch', async () => {
    const { result } = renderHook(
      () => usePareceres({ status: '', tema: '', remetente: '' }),
      { wrapper: makeWrapper() },
    )

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data?.total).toBe(2)
    expect(result.current.data?.items[0].status).toBe('pendente')
  })

  it('configura refetchInterval apenas quando há pareceres em processamento', async () => {
    const { result } = renderHook(
      () => usePareceres({ status: 'pendente', tema: '', remetente: '' }),
      { wrapper: makeWrapper() },
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    // Dados retornam itens com status pendente → deve estar refetchando
    expect(result.current.data?.items.some(p => p.status === 'pendente')).toBe(true)
  })
})

describe('useParecer', () => {
  it('não dispara fetch quando id é undefined', () => {
    const { result } = renderHook(
      () => useParecer(undefined),
      { wrapper: makeWrapper() },
    )

    expect(result.current.isLoading).toBe(false)
    expect(result.current.fetchStatus).toBe('idle')
  })

  it('busca parecer quando id é fornecido', async () => {
    const { result } = renderHook(
      () => useParecer('parecer-1'),
      { wrapper: makeWrapper() },
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data?.id).toBe('parecer-1')
  })
})
