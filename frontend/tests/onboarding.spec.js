import { test, expect } from '@playwright/test';

test.describe('Onboarding Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Continue with Facebook/i }).click();
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /Switch language.*English/i }).click();
  });

  test('displays onboarding header and content', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'The Deets' })).toBeVisible();
    await expect(page.getByText('Help us understand you better')).toBeVisible();
    await expect(page.getByText('Step 1 of 2')).toBeVisible();
  });

  test('displays all disability tags', async ({ page }) => {
    await expect(page.getByText('Wheelchair User')).toBeVisible();
    await expect(page.getByText('Neurodivergent')).toBeVisible();
    await expect(page.getByText('Deaf/HOH')).toBeVisible();
    await expect(page.getByText('Chronic Illness')).toBeVisible();
    await expect(page.getByText('Mental Health')).toBeVisible();
  });

  test('displays mood selector', async ({ page }) => {
    await expect(page.getByText('How are you feeling today?')).toBeVisible();
    await expect(page.getByText('Low Energy')).toBeVisible();
    await expect(page.getByText('Open to Connect')).toBeVisible();
    await expect(page.getByText('Ready to Chat')).toBeVisible();
    await expect(page.getByText('Feeling Bold')).toBeVisible();
  });

  test('Next button is disabled when no tags selected', async ({ page }) => {
    const nextBtn = page.getByRole('button', { name: /Next/i });
    await expect(nextBtn).toBeDisabled();
  });

  test('selecting a tag enables Next button', async ({ page }) => {
    await page.getByRole('button', { name: /Neurodivergent/i }).click();
    
    const nextBtn = page.getByRole('button', { name: /Next/i });
    await expect(nextBtn).toBeEnabled();
  });

  test('shows selected count badge', async ({ page }) => {
    await page.getByRole('button', { name: /Neurodivergent/i }).click();
    await expect(page.getByText('1 selected')).toBeVisible();
    
    await page.getByRole('button', { name: /Chronic Illness/i }).click();
    await expect(page.getByText('2 selected')).toBeVisible();
  });

  test('can toggle tags on and off', async ({ page }) => {
    const tag = page.getByRole('button', { name: /Neurodivergent/i });
    
    // Select
    await tag.click();
    await expect(page.getByText('1 selected')).toBeVisible();
    
    // Deselect
    await tag.click();
    await expect(page.getByText('1 selected')).not.toBeVisible();
  });

  test('Skip button goes to discovery', async ({ page }) => {
    await page.getByRole('button', { name: 'Skip' }).click();
    
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible();
  });

  test('Next button proceeds to preferences', async ({ page }) => {
    await page.getByRole('button', { name: /Neurodivergent/i }).click();
    await page.getByRole('button', { name: /Next/i }).click();
    
    await expect(page.getByRole('heading', { name: 'Looking For' })).toBeVisible();
    await expect(page.getByText('Step 2 of 2')).toBeVisible();
  });
});
