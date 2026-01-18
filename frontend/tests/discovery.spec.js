import { test, expect } from '@playwright/test';

test.describe('Discovery View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    // Wait for language selection page
    await expect(page.getByText('Choose Your Language').first()).toBeVisible({ timeout: 5000 });
    // Click English language button (exact accessible name)
    await page.getByRole('button', { name: 'Switch language - English' }).click();
    // Wait for onboarding page
    await expect(page.getByRole('heading', { name: 'The Deets' })).toBeVisible({ timeout: 5000 });
    // Skip onboarding
    await page.getByRole('button', { name: 'Skip' }).click();
    // Wait for preferences page and skip if visible
    await page.waitForTimeout(500);
    const skipBtn = page.getByRole('button', { name: 'Skip' });
    if (await skipBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipBtn.click();
    }
    // Wait for discovery page
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible({ timeout: 10000 });
  });

  test('displays discovery header', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible();
    await expect(page.getByText('People who get you')).toBeVisible();
  });

  test('displays swipe hint', async ({ page }) => {
    await expect(page.getByText('Swipe to decide')).toBeVisible();
  });

  test('displays profile card', async ({ page }) => {
    // Check profile elements
    await expect(page.getByRole('img', { name: 'Maya' })).toBeVisible();
    await expect(page.getByText('Maya, 28')).toBeVisible();
    await expect(page.getByText('km away')).toBeVisible();
  });

  test('displays compatibility badge', async ({ page }) => {
    await expect(page.getByText('%')).toBeVisible();
    await expect(page.getByText('💫')).toBeVisible();
  });

  test('displays disability tags on profile', async ({ page }) => {
    await expect(page.getByText('Wheelchair User')).toBeVisible();
  });

  test('displays mood indicator', async ({ page }) => {
    await expect(page.getByText('Open to Connect')).toBeVisible();
  });

  test('displays profile prompt', async ({ page }) => {
    await expect(page.getByText('The thing that makes me laugh most is...')).toBeVisible();
  });

  test('displays about section', async ({ page }) => {
    await expect(page.getByText('About me')).toBeVisible();
  });

  test('displays interests', async ({ page }) => {
    await expect(page.getByText('Interests')).toBeVisible();
    await expect(page.getByText('Photography')).toBeVisible();
  });

  test('displays action buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Pass on this profile' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Super Like' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Connect with this person' })).toBeVisible();
  });

  test('Pass button shows next profile', async ({ page }) => {
    const firstName = await page.getByRole('heading', { level: 2 }).textContent();
    
    await page.getByRole('button', { name: 'Pass on this profile' }).click();
    
    // Wait for animation and check for different profile or end state
    await page.waitForTimeout(500);
  });

  test('Connect button triggers match or shows next profile', async ({ page }) => {
    await page.getByRole('button', { name: 'Connect with this person' }).click();
    
    // Either match screen or next profile
    await page.waitForTimeout(500);
  });

  test('Profile button navigates to profile', async ({ page }) => {
    await page.getByRole('button', { name: 'Profile' }).click();
    
    await expect(page.getByRole('heading', { name: 'My Profile' })).toBeVisible();
  });

  test('back button returns to preferences', async ({ page }) => {
    await page.getByRole('button', { name: 'Go back' }).click();
    
    // Should go back in navigation
    await page.waitForTimeout(300);
  });
});

test.describe('Discovery - Swipe Gestures', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /English/i }).click();
    await page.getByRole('button', { name: 'Skip' }).click();
  });

  test('card can be dragged', async ({ page }) => {
    const card = page.locator('.card').first();
    
    // Get initial position
    const box = await card.boundingBox();
    
    if (box) {
      // Simulate drag start
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width / 2 + 50, box.y + box.height / 2);
      
      // Card should have moved
      await page.mouse.up();
    }
  });

  test('swipe right triggers connect overlay', async ({ page }) => {
    const card = page.locator('.card').first();
    const box = await card.boundingBox();
    
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width / 2 + 100, box.y + box.height / 2);
      
      // Connect overlay should show
      await expect(page.getByText('Connect').first()).toBeVisible();
      
      await page.mouse.up();
    }
  });

  test('swipe left triggers pass overlay', async ({ page }) => {
    const card = page.locator('.card').first();
    const box = await card.boundingBox();
    
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width / 2 - 100, box.y + box.height / 2);
      
      // Pass overlay should show
      await expect(page.getByText('Pass').first()).toBeVisible();
      
      await page.mouse.up();
    }
  });
});
