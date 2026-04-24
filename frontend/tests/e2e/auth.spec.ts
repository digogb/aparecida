import { test, expect } from '@playwright/test'

test.describe('Autenticação', () => {
  test('login com credenciais válidas redireciona para dashboard', async ({ page }) => {
    await page.goto('/login')

    await page.getByLabel('Email').fill('harvey@pearsonhardman.com')
    await page.getByLabel('Senha').fill('123456')
    await page.getByRole('button', { name: 'Entrar' }).click()

    await expect(page).toHaveURL(/\/$|\/dashboard/)
    await expect(page.getByRole('navigation')).toBeVisible()
  })

  test('login com credenciais inválidas exibe mensagem de erro', async ({ page }) => {
    await page.goto('/login')

    await page.getByLabel('Email').fill('usuario@errado.com')
    await page.getByLabel('Senha').fill('senhaerrada')
    await page.getByRole('button', { name: 'Entrar' }).click()

    await expect(page.getByText('Email ou senha inválidos')).toBeVisible()
    await expect(page).toHaveURL(/\/login/)
  })

  test('logout redireciona para a tela de login', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('harvey@pearsonhardman.com')
    await page.getByLabel('Senha').fill('123456')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page).not.toHaveURL(/\/login/)

    await page.getByRole('button', { name: 'Sair' }).click()

    await expect(page).toHaveURL(/\/login/)
  })

  test('acesso direto a rota protegida sem token redireciona para login', async ({ page }) => {
    await page.goto('/login')
    await page.evaluate(() => localStorage.removeItem('token'))

    await page.goto('/pareceres')

    await expect(page).toHaveURL(/\/login/)
  })
})
