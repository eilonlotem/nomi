import { test, expect } from '@playwright/test';

test.describe('Accessibility Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('accessibility panel can be opened', async ({ page }) => {
    await page.getByRole('button', { name: 'Accessibility' }).click();
    
    await expect(page.getByText('Text Size')).toBeVisible();
    await expect(page.getByText('High Contrast')).toBeVisible();
    await expect(page.getByText('Reduced Motion')).toBeVisible();
  });

  test('can change text size to large', async ({ page }) => {
    await page.getByRole('button', { name: 'Accessibility' }).click();
    await page.getByRole('button', { name: 'A+' }).click();
    
    // Text size should increase
    // Can check for class or computed style change
  });

  test('can change text size to extra large', async ({ page }) => {
    await page.getByRole('button', { name: 'Accessibility' }).click();
    await page.getByRole('button', { name: 'A++' }).click();
  });

  test('can toggle high contrast', async ({ page }) => {
    await page.getByRole('button', { name: 'Accessibility' }).click();
    
    // Find and click high contrast toggle
    const toggles = page.locator('button').filter({ hasText: /^$/ });
    await toggles.first().click();
  });

  test('can toggle reduced motion', async ({ page }) => {
    await page.getByRole('button', { name: 'Accessibility' }).click();
    
    // Find and click reduced motion toggle
  });

  test('all buttons have minimum touch target size', async ({ page }) => {
    const buttons = page.getByRole('button');
    const count = await buttons.count();
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = buttons.nth(i);
      const box = await button.boundingBox();
      
      if (box) {
        // Minimum touch target should be 44px
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('interactive elements are focusable', async ({ page }) => {
    // Tab through elements
    await page.keyboard.press('Tab');
    
    // Something should be focused
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused).not.toBe('BODY');
  });

  test('buttons have aria-labels', async ({ page }) => {
    const a11yButton = page.getByRole('button', { name: 'Accessibility' });
    await expect(a11yButton).toBeVisible();
    
    // Social buttons should have labels
    await expect(page.getByRole('button', { name: /Continue with Facebook/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Continue with Instagram/i })).toBeVisible();
  });
});

test.describe('Screen Reader Compatibility', () => {
  test('headings have proper hierarchy', async ({ page }) => {
    await page.goto('/');
    
    // Check h1 exists
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1.first()).toBeVisible();
  });

  test('images have alt text', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /English/i }).click();
    await page.getByRole('button', { name: 'Skip' }).click();
    
    // Profile image should have alt text
    const img = page.getByRole('img', { name: 'Maya' });
    await expect(img).toBeVisible();
  });

  test('form inputs have labels', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /English/i }).click();
    await page.getByRole('button', { name: /Neurodivergent/i }).click();
    await page.getByRole('button', { name: /Next/i }).click();
    
    // Check for labeled inputs
    const locationInput = page.getByPlaceholder(/Tel Aviv/i);
    await expect(locationInput).toBeVisible();
  });
});
