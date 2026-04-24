import { describe, expect, it } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../__tests__/msw/server'
import { deleteParecer, fetchParecer, fetchPareceres } from './parecerApi'

describe('fetchPareceres', () => {
  it('retorna lista paginada com total correto', async () => {
    const result = await fetchPareceres({ status: '', tema: '', remetente: '' })

    expect(result.total).toBe(2)
    expect(result.items).toHaveLength(2)
    expect(result.items[0].id).toBe('parecer-1')
  })

  it('envia status e tema como query params', async () => {
    let url: string | undefined

    server.use(
      http.get('/api/parecer-requests', ({ request }) => {
        url = request.url
        return HttpResponse.json({ items: [], total: 0, limit: 100, offset: 0 })
      }),
    )

    await fetchPareceres({ status: 'pendente', tema: 'licitacao', remetente: '' })

    expect(url).toContain('status=pendente')
    expect(url).toContain('tema=licitacao')
  })

  it('não inclui params vazios na query string', async () => {
    let url: string | undefined

    server.use(
      http.get('/api/parecer-requests', ({ request }) => {
        url = request.url
        return HttpResponse.json({ items: [], total: 0, limit: 100, offset: 0 })
      }),
    )

    await fetchPareceres({ status: '', tema: '', remetente: '' })

    expect(url).not.toContain('status=')
    expect(url).not.toContain('tema=')
  })
})

describe('fetchParecer', () => {
  it('retorna detalhe por ID com versions vazia', async () => {
    const result = await fetchParecer('parecer-1')

    expect(result.id).toBe('parecer-1')
    expect(result.versions).toEqual([])
    expect(result.attachments).toEqual([])
  })
})

describe('deleteParecer', () => {
  it('resolve sem erro em caso de sucesso (204)', async () => {
    await expect(deleteParecer('parecer-1')).resolves.toBeUndefined()
  })

  it('lança erro se API retornar 500', async () => {
    server.use(
      http.delete('/api/parecer-requests/:id', () => {
        return HttpResponse.json({ detail: 'erro interno' }, { status: 500 })
      }),
    )

    await expect(deleteParecer('parecer-1')).rejects.toThrow()
  })
})
