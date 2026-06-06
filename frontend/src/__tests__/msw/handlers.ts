import { http, HttpResponse } from 'msw'
import { parecerFixture, parecerListFixture } from '../fixtures/parecer'

export const handlers = [
  // Pareceres
  http.get('/api/parecer-requests', () => {
    return HttpResponse.json(parecerListFixture)
  }),

  http.get('/api/parecer-requests/:id', ({ params }) => {
    return HttpResponse.json({ ...parecerFixture, id: params.id as string })
  }),

  http.delete('/api/parecer-requests/:id', () => {
    return new HttpResponse(null, { status: 204 })
  }),

  // Auth
  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json() as { email: string; password: string }
    if (body.email === 'matheus@ione.adv.br' && body.password === '123456') {
      return HttpResponse.json({ access_token: 'token-valido', token_type: 'bearer' })
    }
    return HttpResponse.json({ detail: 'Credenciais inválidas' }, { status: 401 })
  }),

  http.get('/api/auth/me', ({ request }) => {
    const auth = request.headers.get('Authorization')
    if (!auth?.startsWith('Bearer ')) {
      return HttpResponse.json({ detail: 'Não autenticado' }, { status: 401 })
    }
    return HttpResponse.json({
      id: 'user-1',
      name: 'Dr. Advogado Teste',
      email: 'advogado@escritorio.com',
      role: 'advogado',
    })
  }),
]
