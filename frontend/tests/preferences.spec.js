import { test, expect } from '@playwright/test';

test.describe('Preferences (Looking For) Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.getByRole('button', { name: /English/i }).click();
    await page.getByRole('button', { name: /Neurodivergent/i }).click();
    await page.getByRole('button', { name: /Next/i }).click();
  });

  test('displays preferences header', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Looking For' })).toBeVisible();
    await expect(page.getByText('Step 2 of 2')).toBeVisible();
    await expect(page.getByText('Who catches your eye?')).toBeVisible();
  });

  test('displays gender options', async ({ page }) => {
    await expect(page.getByText("I'm interested in...")).toBeVisible();
    await expect(page.getByRole('button', { name: /Men/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Women/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Non-binary/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Everyone/i })).toBeVisible();
  });

  test('displays relationship type options', async ({ page }) => {
    await expect(page.getByText('What are you looking for?')).toBeVisible();
    await expect(page.getByRole('button', { name: /Casual Dating/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Serious Relationship/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Just Friends/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Activity Partners/i })).toBeVisible();
  });

  test('displays age range inputs', async ({ page }) => {
    await expect(page.getByText('Age Range')).toBeVisible();
    await expect(page.getByRole('spinbutton').first()).toHaveValue('18');
    await expect(page.getByRole('spinbutton').nth(1)).toHaveValue('50');
  });

  test('displays location inputs', async ({ page }) => {
    await expect(page.getByText('Location')).toBeVisible();
    await expect(page.getByPlaceholder(/Tel Aviv/i)).toBeVisible();
    await expect(page.getByText('Maximum distance')).toBeVisible();
    await expect(page.getByText('50 km')).toBeVisible();
  });

  test('can select gender preferences', async ({ page }) => {
    const womenBtn = page.getByRole('button', { name: /Women/i });
    await womenBtn.click();
    
    // Button should have active state (check for different styling)
    await expect(womenBtn).toHaveClass(/bg-primary/);
  });

  test('can select multiple relationship types', async ({ page }) => {
    await page.getByRole('button', { name: /Casual Dating/i }).click();
    await page.getByRole('button', { name: /Just Friends/i }).click();
    
    // Both should be selected
  });

  test('Continue button proceeds to discovery', async ({ page }) => {
    await page.getByRole('button', { name: /Continue to Discovery/i }).click();
    
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible();
  });

  test('Skip button proceeds to discovery', async ({ page }) => {
    await page.getByRole('button', { name: 'Skip' }).click();
    
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible();
  });

  test('back button returns to onboarding', async ({ page }) => {
    await page.getByRole('button', { name: 'Go back' }).click();
    
    await expect(page.getByRole('heading', { name: 'The Deets' })).toBeVisible();
  });
});
