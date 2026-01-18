import { test, expect } from '@playwright/test';

test.describe('Language Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Login first
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
  });

  test('displays all available languages', async ({ page }) => {
    await expect(page.getByText('English')).toBeVisible();
    await expect(page.getByText('עברית')).toBeVisible();
    await expect(page.getByText('Español')).toBeVisible();
    await expect(page.getByText('Français')).toBeVisible();
    await expect(page.getByText('العربية')).toBeVisible();
  });

  test('shows language flags', async ({ page }) => {
    await expect(page.getByText('🇬🇧')).toBeVisible();
    await expect(page.getByText('🇮🇱')).toBeVisible();
    await expect(page.getByText('🇪🇸')).toBeVisible();
    await expect(page.getByText('🇫🇷')).toBeVisible();
    await expect(page.getByText('🇸🇦')).toBeVisible();
  });

  test('selecting English proceeds to onboarding', async ({ page }) => {
    await page.getByRole('button', { name: /Switch language.*English/i }).click();
    
    // Should show onboarding
    await expect(page.getByRole('heading', { name: 'The Deets' })).toBeVisible();
    await expect(page.getByText('Step 1 of 2')).toBeVisible();
  });

  test('selecting Hebrew sets RTL direction', async ({ page }) => {
    await page.getByRole('button', { name: /Switch language.*עברית/i }).click();
    
    // Check RTL is applied
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'rtl');
  });

  test('selecting Arabic sets RTL direction', async ({ page }) => {
    await page.getByRole('button', { name: /Switch language.*العربية/i }).click();
    
    // Check RTL is applied
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'rtl');
  });

  test('back button returns to login', async ({ page }) => {
    await page.getByRole('button', { name: 'Go back' }).click();
    
    // Should be back at login
    await expect(page.getByRole('heading', { name: 'nomi' })).toBeVisible();
  });
});
