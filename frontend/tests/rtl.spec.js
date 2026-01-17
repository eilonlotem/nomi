import { test, expect } from '@playwright/test';

test.describe('RTL (Right-to-Left) Support', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
  });

  test('Hebrew selection sets RTL direction', async ({ page }) => {
    await page.getByRole('button', { name: /עברית/i }).click();
    
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'rtl');
  });

  test('Arabic selection sets RTL direction', async ({ page }) => {
    await page.getByRole('button', { name: /العربية/i }).click();
    
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'rtl');
  });

  test('English selection sets LTR direction', async ({ page }) => {
    await page.getByRole('button', { name: /English/i }).click();
    
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'ltr');
  });

  test('Spanish selection sets LTR direction', async ({ page }) => {
    await page.getByRole('button', { name: /Español/i }).click();
    
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'ltr');
  });

  test('French selection sets LTR direction', async ({ page }) => {
    await page.getByRole('button', { name: /Français/i }).click();
    
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'ltr');
  });
});

test.describe('Hebrew Language UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /עברית/i }).click();
  });

  test('onboarding shows Hebrew text', async ({ page }) => {
    await expect(page.getByText('הפרטים')).toBeVisible(); // "The Deets" in Hebrew
    await expect(page.getByText('שלב 1 מתוך 2')).toBeVisible(); // "Step 1 of 2"
  });

  test('tags are in Hebrew', async ({ page }) => {
    await expect(page.getByText('מתנייד בכיסא גלגלים')).toBeVisible(); // Wheelchair User
    await expect(page.getByText('נוירו-דיברגנטי')).toBeVisible(); // Neurodivergent
  });

  test('moods are in Hebrew', async ({ page }) => {
    await expect(page.getByText('איך את/ה מרגיש/ה היום?')).toBeVisible(); // How are you feeling?
    await expect(page.getByText('אנרגיה נמוכה')).toBeVisible(); // Low Energy
  });

  test('back arrow flips in RTL', async ({ page }) => {
    const backButton = page.getByRole('button', { name: /חזרה/i });
    // In RTL, the arrow should flip (use flip-rtl class)
    const svg = backButton.locator('svg');
    await expect(svg).toHaveClass(/flip-rtl/);
  });

  test('preferences page shows Hebrew', async ({ page }) => {
    await page.getByRole('button', { name: /נוירו-דיברגנטי/i }).click();
    await page.getByRole('button', { name: /הבא/i }).click();
    
    await expect(page.getByText('מחפש/ת')).toBeVisible(); // Looking For
    await expect(page.getByText('מתעניין/ת ב...')).toBeVisible(); // Interested in
  });
});

test.describe('Arabic Language UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /العربية/i }).click();
  });

  test('onboarding shows Arabic text', async ({ page }) => {
    await expect(page.getByText('التفاصيل')).toBeVisible(); // The Deets
  });

  test('RTL layout is applied', async ({ page }) => {
    const body = page.locator('body');
    await expect(body).toHaveAttribute('dir', 'rtl');
  });
});

test.describe('RTL Layout Verification', () => {
  test('buttons align correctly in RTL', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /עברית/i }).click();
    
    // Skip button should be on left in RTL
    const skipButton = page.getByRole('button', { name: /דלג/i });
    const box = await skipButton.boundingBox();
    const viewport = page.viewportSize();
    
    if (box && viewport) {
      // In RTL, skip button should be on the left side
      expect(box.x).toBeLessThan(viewport.width / 2);
    }
  });
});
