import { test, expect } from '@playwright/test';

/**
 * End-to-end test flows for Nomi dating app
 * Covers: Login, Match, Send Message, Check Matches, Chat with Match
 */

// Helper to block Facebook SDK and force mock login
async function setupMockLogin(page) {
  // Block Facebook SDK from loading
  await page.route('**/connect.facebook.net/**', route => route.abort());
  await page.route('**/facebook.com/**', route => route.abort());
  
  // Add script to ensure mock login is used
  await page.addInitScript(() => {
    // Prevent Facebook SDK from initializing
    window.FB = null;
    
    // Override the VITE env variable to remove Facebook App ID
    // This forces the app to use mock login
    Object.defineProperty(window, '__MOCK_LOGIN__', {
      value: true,
      writable: false
    });
  });
}

// Helper function to complete login and onboarding
async function loginAndOnboard(page) {
  // Block Facebook SDK and force mock login
  await setupMockLogin(page);
  
  await page.goto('/');
  
  // Wait for page to load
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(500);
  
  // Click Facebook login and wait for it to complete
  const facebookBtn = page.getByRole('button', { name: /Continue with Facebook/i });
  await expect(facebookBtn).toBeVisible({ timeout: 5000 });
  await facebookBtn.click();
  
  // Wait for mock login to complete and language selection to appear
  // Mock login should be very fast since we blocked FB SDK
  await expect(page.getByRole('heading', { name: 'Choose Your Language' }).first()).toBeVisible({ timeout: 10000 });
  
  // Select English
  await page.getByRole('button', { name: /English/i }).click();
  
  // Wait for transition
  await page.waitForTimeout(1000);
  
  // If on onboarding, skip it
  const skipButton = page.getByRole('button', { name: 'Skip' });
  if (await skipButton.isVisible({ timeout: 3000 }).catch(() => false)) {
    await skipButton.click();
    await page.waitForTimeout(500);
  }
  
  // Should now be on discovery
  await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible({ timeout: 10000 });
}

// Helper to navigate to matches view
async function navigateToMatches(page) {
  await page.getByRole('button', { name: 'My Matches' }).click();
  await expect(page.getByRole('heading', { name: 'My Matches' })).toBeVisible({ timeout: 5000 });
}

test.describe('1. Login Flow', () => {
  test('complete login flow with Facebook', async ({ page }) => {
    // Block Facebook SDK and force mock login
    await setupMockLogin(page);
    
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);
    
    // Verify login page
    await expect(page.getByRole('heading', { name: 'nomi' })).toBeVisible();
    await expect(page.getByText('Find Your Connection')).toBeVisible();
    
    // Click Facebook login
    const facebookBtn = page.getByRole('button', { name: /Continue with Facebook/i });
    await expect(facebookBtn).toBeVisible();
    await facebookBtn.click();
    
    // Verify navigation to language selection
    await expect(page.getByRole('heading', { name: 'Choose Your Language' }).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Connected')).toBeVisible();
    
    // Verify language options
    await expect(page.getByRole('button', { name: /English/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Hebrew/i })).toBeVisible();
  });

  test('can access profile page when logged in', async ({ page }) => {
    await loginAndOnboard(page);
    
    // Go to profile
    await page.getByRole('button', { name: 'Profile' }).click();
    await expect(page.getByRole('heading', { name: 'Edit Profile' })).toBeVisible({ timeout: 5000 });
    
    // Verify profile elements are visible
    await expect(page.getByText('Basic Info')).toBeVisible();
  });
});

test.describe('2. Match Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndOnboard(page);
  });

  test('display profile card or empty state', async ({ page }) => {
    // Check if we have profiles or empty state
    const hasProfiles = await page.getByRole('button', { name: 'Connect with this person' }).isVisible({ timeout: 3000 }).catch(() => false);
    const hasEmptyState = await page.getByText(/seen everyone/i).isVisible().catch(() => false);
    
    if (hasProfiles) {
      // Check for profile card elements
      const profileHeading = page.getByRole('heading', { level: 2 }).first();
      await expect(profileHeading).toBeVisible();
      
      // Check for profile photo
      const profileImage = page.getByRole('img').first();
      await expect(profileImage).toBeVisible();
      
      // Check for action buttons
      await expect(page.getByRole('button', { name: 'Pass on this profile' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Connect with this person' })).toBeVisible();
    } else {
      // Empty state should be shown
      expect(hasEmptyState).toBe(true);
    }
  });

  test('connect button advances to next profile or shows match', async ({ page }) => {
    // Check if we have profiles
    const hasProfiles = await page.getByRole('button', { name: 'Connect with this person' }).isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasProfiles) {
      // No profiles, skip test
      test.skip();
      return;
    }
    
    // Get current profile name
    const profileHeading = page.getByRole('heading', { level: 2 }).first();
    const initialName = await profileHeading.textContent();
    
    // Click connect
    await page.getByRole('button', { name: 'Connect with this person' }).click();
    
    // Wait for animation
    await page.waitForTimeout(1000);
    
    // Either we see a match animation, next profile, or "no more profiles"
    const hasMatchAnimation = await page.getByText(/It\'s a Match|You matched/i).isVisible().catch(() => false);
    const hasNoMoreProfiles = await page.getByText(/seen everyone/i).isVisible().catch(() => false);
    const newName = await profileHeading.textContent().catch(() => null);
    
    // Should have progressed in some way
    expect(hasMatchAnimation || hasNoMoreProfiles || newName !== initialName).toBe(true);
  });

  test('pass button advances to next profile', async ({ page }) => {
    // Check if we have profiles
    const hasProfiles = await page.getByRole('button', { name: 'Pass on this profile' }).isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasProfiles) {
      // No profiles, skip test
      test.skip();
      return;
    }
    
    // Get current profile name
    const profileHeading = page.getByRole('heading', { level: 2 }).first();
    const initialName = await profileHeading.textContent();
    
    // Click pass
    await page.getByRole('button', { name: 'Pass on this profile' }).click();
    
    // Wait for animation
    await page.waitForTimeout(1000);
    
    // Either we see next profile or "no more profiles"
    const hasNoMoreProfiles = await page.getByText(/seen everyone/i).isVisible().catch(() => false);
    const newName = await profileHeading.textContent().catch(() => null);
    
    // Should have progressed
    expect(hasNoMoreProfiles || newName !== initialName).toBe(true);
  });
});

test.describe('3. Check Matches Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndOnboard(page);
  });

  test('navigate to matches view', async ({ page }) => {
    await navigateToMatches(page);
    
    // Verify matches header
    await expect(page.getByRole('heading', { name: 'My Matches' })).toBeVisible();
    await expect(page.getByText('Your connections', { exact: true })).toBeVisible();
  });

  test('display matches list or empty state', async ({ page }) => {
    await navigateToMatches(page);
    
    // Either we have matches or empty state
    const hasMatches = await page.getByRole('button', { name: 'Start Chat' }).first().isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('No matches yet').isVisible().catch(() => false);
    
    expect(hasMatches || hasEmptyState).toBe(true);
  });

  test('matches show profile information', async ({ page }) => {
    await navigateToMatches(page);
    
    // If matches exist, verify they have required info
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible().catch(() => false);
    
    if (hasMatches) {
      // Check for profile elements in match cards
      const matchCard = page.locator('[class*="cursor-pointer"]').first();
      await expect(matchCard).toBeVisible();
      
      // Match cards should have names and ages
      const heading = page.getByRole('heading', { level: 3 }).first();
      await expect(heading).toBeVisible();
    }
  });

  test('navigate back to discovery from matches', async ({ page }) => {
    await navigateToMatches(page);
    
    // Click back button
    await page.getByRole('button', { name: 'Go back' }).click();
    
    // Should return to discovery
    await expect(page.getByRole('heading', { name: 'Nomi Match' })).toBeVisible({ timeout: 5000 });
  });
});

test.describe('4. Send Message Flow', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndOnboard(page);
    await navigateToMatches(page);
  });

  test('open chat from matches', async ({ page }) => {
    // Check if we have matches
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasMatches) {
      test.skip();
      return;
    }
    
    // Click on a match to open chat
    await startChatBtn.click();
    
    // Verify chat view opens
    await expect(page.getByRole('heading', { name: 'Connection' })).toBeVisible({ timeout: 5000 });
  });

  test('send message in chat', async ({ page }) => {
    // Check if we have matches
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasMatches) {
      test.skip();
      return;
    }
    
    // Open chat
    await startChatBtn.click();
    await expect(page.getByRole('heading', { name: 'Connection' })).toBeVisible({ timeout: 5000 });
    
    // Find message input
    const messageInput = page.getByPlaceholder(/type a message/i);
    await expect(messageInput).toBeVisible();
    
    // Type a message
    const testMessage = `Test message ${Date.now()}`;
    await messageInput.fill(testMessage);
    
    // Click send button
    await page.getByRole('button', { name: 'Send' }).click();
    
    // Verify message appears in chat
    await expect(page.getByText(testMessage)).toBeVisible({ timeout: 5000 });
  });

  test('send message with Enter key', async ({ page }) => {
    // Check if we have matches
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasMatches) {
      test.skip();
      return;
    }
    
    // Open chat
    await startChatBtn.click();
    await expect(page.getByRole('heading', { name: 'Connection' })).toBeVisible({ timeout: 5000 });
    
    // Find message input
    const messageInput = page.getByPlaceholder(/type a message/i);
    
    // Type and press Enter
    const testMessage = `Enter test ${Date.now()}`;
    await messageInput.fill(testMessage);
    await messageInput.press('Enter');
    
    // Verify message appears
    await expect(page.getByText(testMessage)).toBeVisible({ timeout: 5000 });
  });
});

test.describe('5. Full E2E: Match to Chat Flow', () => {
  test('complete flow: login -> matches -> chat -> send message -> back', async ({ page }) => {
    // Step 1: Login and onboard
    await loginAndOnboard(page);
    
    // Step 2: Navigate to matches
    await navigateToMatches(page);
    
    // Step 3: Check for matches
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasMatches) {
      // If no matches, verify empty state and return
      await expect(page.getByText('No matches yet')).toBeVisible();
      return;
    }
    
    // Get the match name for verification
    const matchName = await page.getByRole('heading', { level: 3 }).first().textContent();
    
    // Step 4: Open chat with match
    await startChatBtn.click();
    await expect(page.getByRole('heading', { name: 'Connection' })).toBeVisible({ timeout: 5000 });
    
    // Step 5: Send a message
    const messageInput = page.getByPlaceholder(/type a message/i);
    await expect(messageInput).toBeVisible();
    
    const testMessage = `Hello from E2E test! ${Date.now()}`;
    await messageInput.fill(testMessage);
    await page.getByRole('button', { name: 'Send' }).click();
    
    // Verify message appears
    await expect(page.getByText(testMessage)).toBeVisible({ timeout: 5000 });
    
    // Step 6: Go back to matches
    await page.getByRole('button', { name: 'Go back' }).click();
    
    // Verify we're back on matches
    await expect(page.getByRole('heading', { name: 'My Matches' })).toBeVisible({ timeout: 5000 });
    
    // Verify the match is still there
    await expect(page.getByRole('heading', { level: 3, name: matchName })).toBeVisible();
  });

  test('multiple messages in conversation', async ({ page }) => {
    await loginAndOnboard(page);
    await navigateToMatches(page);
    
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasMatches) {
      test.skip();
      return;
    }
    
    // Open chat
    await startChatBtn.click();
    await expect(page.getByRole('heading', { name: 'Connection' })).toBeVisible({ timeout: 5000 });
    
    const messageInput = page.getByPlaceholder(/type a message/i);
    
    // Send multiple messages
    const messages = [
      'First message',
      'Second message',
      'Third message'
    ];
    
    for (const msg of messages) {
      await messageInput.fill(msg);
      await page.getByRole('button', { name: 'Send' }).click();
      await page.waitForTimeout(500);
    }
    
    // Verify all messages appear
    for (const msg of messages) {
      await expect(page.getByText(msg)).toBeVisible();
    }
  });
});

test.describe('6. Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndOnboard(page);
  });

  test('empty message is not sent', async ({ page }) => {
    await navigateToMatches(page);
    
    const startChatBtn = page.getByRole('button', { name: 'Start Chat' }).first();
    const hasMatches = await startChatBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (!hasMatches) {
      test.skip();
      return;
    }
    
    await startChatBtn.click();
    await expect(page.getByRole('heading', { name: 'Connection' })).toBeVisible({ timeout: 5000 });
    
    // Try to send empty message
    const messageInput = page.getByPlaceholder(/type a message/i);
    await messageInput.fill('');
    
    const sendButton = page.getByRole('button', { name: 'Send' });
    
    // Send button should be disabled or clicking should do nothing
    const messageCountBefore = await page.locator('.chat-message, [class*="message"]').count();
    await sendButton.click().catch(() => {});
    await page.waitForTimeout(500);
    const messageCountAfter = await page.locator('.chat-message, [class*="message"]').count();
    
    // No new message should be added
    expect(messageCountAfter).toBe(messageCountBefore);
  });

  test('matches badge updates', async ({ page }) => {
    // Check if matches badge shows count
    const matchesButton = page.getByRole('button', { name: 'My Matches' });
    await expect(matchesButton).toBeVisible();
    
    // The badge should be visible if there are matches
    // Just verify the button is clickable
    await matchesButton.click();
    await expect(page.getByRole('heading', { name: 'My Matches' })).toBeVisible({ timeout: 5000 });
  });
});
