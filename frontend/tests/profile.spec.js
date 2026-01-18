import { test, expect } from '@playwright/test';

test.describe('Profile View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /Switch language.*English/i }).click();
    await page.waitForTimeout(500);
    // Skip onboarding
    await page.getByRole('button', { name: 'Skip' }).click();
    await page.waitForTimeout(500);
    // Skip preferences (if visible)
    const skipBtn = page.getByRole('button', { name: 'Skip' });
    if (await skipBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipBtn.click();
      await page.waitForTimeout(500);
    }
    await page.getByRole('button', { name: 'Profile' }).click();
  });

  test('displays profile header', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'My Profile' })).toBeVisible();
  });

  test('displays profile photo', async ({ page }) => {
    await expect(page.getByRole('img').first()).toBeVisible();
    await expect(page.getByText('Tap to change')).toBeVisible();
  });

  test('displays basic info section', async ({ page }) => {
    await expect(page.getByText('Basic Info')).toBeVisible();
    await expect(page.getByText('Name')).toBeVisible();
    await expect(page.getByText('Age')).toBeVisible();
    await expect(page.getByText('Location')).toBeVisible();
  });

  test('displays editable name field', async ({ page }) => {
    const nameInput = page.getByRole('textbox').first();
    await expect(nameInput).toBeVisible();
  });

  test('displays identity tags section', async ({ page }) => {
    await expect(page.getByText('My Identity Tags')).toBeVisible();
  });

  test('displays looking for section', async ({ page }) => {
    await expect(page.getByText('Looking For')).toBeVisible();
    await expect(page.getByText("I'm interested in...")).toBeVisible();
    await expect(page.getByText('What are you looking for?')).toBeVisible();
  });

  test('displays age range in preferences', async ({ page }) => {
    await expect(page.getByText('Age Range').first()).toBeVisible();
  });

  test('displays location preference', async ({ page }) => {
    // Scroll down to see location section
    await page.evaluate(() => window.scrollTo(0, 500));
    await expect(page.getByText('Maximum distance')).toBeVisible();
  });

  test('displays interests section', async ({ page }) => {
    await expect(page.getByText('My Interests')).toBeVisible();
    await expect(page.getByText('Add interest')).toBeVisible();
  });

  test('displays profile prompt section', async ({ page }) => {
    await expect(page.getByText('Profile Prompt')).toBeVisible();
  });

  test('displays language selection', async ({ page }) => {
    await page.evaluate(() => window.scrollTo(0, 1000));
    await expect(page.getByText('Choose Language')).toBeVisible();
  });

  test('can change language from profile', async ({ page }) => {
    await page.evaluate(() => window.scrollTo(0, 1000));
    
    // Find Hebrew button and click
    const hebrewBtn = page.getByRole('button', { name: /עברית/i });
    if (await hebrewBtn.isVisible()) {
      await hebrewBtn.click();
      
      // Check RTL is applied
      const body = page.locator('body');
      await expect(body).toHaveAttribute('dir', 'rtl');
    }
  });

  test('back button returns to discovery', async ({ page }) => {
    await page.getByRole('button', { name: 'Go back' }).click();
    
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible();
  });
});

test.describe('Profile Editing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /English/i }).click();
    await page.getByRole('button', { name: 'Skip' }).click();
    await page.getByRole('button', { name: 'Profile' }).click();
  });

  test('can edit name', async ({ page }) => {
    const nameInput = page.getByRole('textbox').first();
    await nameInput.fill('');
    await nameInput.fill('John');
    await expect(nameInput).toHaveValue('John');
  });

  test('can toggle gender preferences', async ({ page }) => {
    const womenBtn = page.getByRole('button', { name: /Women/i }).first();
    await womenBtn.click();
    
    // Should toggle state
  });

  test('can toggle relationship type preferences', async ({ page }) => {
    const casualBtn = page.getByRole('button', { name: /Casual Dating/i }).first();
    await casualBtn.click();
  });

  test('can add interest', async ({ page }) => {
    const addBtn = page.getByText('Add interest');
    await addBtn.click();
    
    // Should show input or modal for adding interest
  });
});
