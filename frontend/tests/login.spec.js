import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays login page with branding', async ({ page }) => {
    // Check logo and branding
    await expect(page.getByRole('heading', { name: 'nomi' })).toBeVisible();
    await expect(page.getByText('Find Your Connection')).toBeVisible();
    await expect(page.getByText('Because everyone deserves love')).toBeVisible();
    
    // Check stats are displayed
    await expect(page.getByText('12K+')).toBeVisible();
    await expect(page.getByText('Members')).toBeVisible();
  });

  test('shows social login buttons', async ({ page }) => {
    const facebookBtn = page.getByRole('button', { name: /Continue with Facebook/i });
    const instagramBtn = page.getByRole('button', { name: /Continue with Instagram/i });
    
    await expect(facebookBtn).toBeVisible();
    await expect(instagramBtn).toBeVisible();
  });

  test('Facebook login navigates to language selection', async ({ page }) => {
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    
    // Should show language selection
    await expect(page.getByRole('heading', { name: 'Choose Your Language' })).toBeVisible();
    await expect(page.getByText('Connected')).toBeVisible();
  });

  test('Instagram login navigates to language selection', async ({ page }) => {
    await page.getByRole('button', { name: /Continue with Instagram/i }).click();
    
    // Should show language selection
    await expect(page.getByRole('heading', { name: 'Choose Your Language' })).toBeVisible();
  });

  test('shows terms and privacy links', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Terms' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Privacy Policy' })).toBeVisible();
  });

  test('accessibility settings button is visible', async ({ page }) => {
    const a11yButton = page.getByRole('button', { name: 'Accessibility' });
    await expect(a11yButton).toBeVisible();
  });
});
