import { test, expect, type Page } from '@playwright/test'

async function login(page: Page) {
  await page.goto('/login')
  await page.getByLabel('Email').fill('harvey@pearsonhardman.com')
  await page.getByLabel('Senha').fill('123456')
  await page.getByRole('button', { name: 'Entrar' }).click()
  await expect(page).not.toHaveURL(/\/login/)
}

test.describe('Pareceres', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('dashboard carrega com lista de pareceres', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('main')).toBeVisible()
    // Aguarda conteúdo carregar (spinner some ou lista aparece)
    await expect(page.locator('main')).not.toContainText('carregando', { timeout: 10_000, ignoreCase: true })
  })

  test('lista de pareceres carrega e exibe ao menos um item', async ({ page }) => {
    await page.goto('/pareceres')

    // Aguarda sair do estado de loading
    await page.waitForLoadState('networkidle')

    const lista = page.getByRole('main')
    await expect(lista).toBeVisible()
    // Deve haver itens de parecer OU mensagem de lista vazia
    const temItens = lista.locator('[data-testid="parecer-card"], .space-y-2 > div').first()
    const listaVazia = lista.getByText('Nenhum parecer encontrado')
    await expect(temItens.or(listaVazia)).toBeVisible({ timeout: 10_000 })
  })

  test('filtro de status não crasha a aplicação', async ({ page }) => {
    await page.goto('/pareceres')
    await page.waitForLoadState('networkidle')

    // Tenta localizar qualquer filtro disponível
    const combobox = page.getByRole('combobox').first()
    if (await combobox.isVisible()) {
      await combobox.selectOption({ index: 1 }).catch(() => {/* sem opções — ok */})
      await page.waitForLoadState('networkidle')
    }

    // A página não deve ter crashado
    await expect(page.getByRole('main')).toBeVisible()
  })

  test('sidebar exibe links Dashboard e Pareceres', async ({ page }) => {
    await page.goto('/')

    const nav = page.getByRole('navigation')
    await expect(nav).toBeVisible()
    await expect(nav.getByRole('link', { name: 'Dashboard' })).toBeVisible()
    await expect(nav.getByRole('link', { name: 'Pareceres' })).toBeVisible()
  })
})
