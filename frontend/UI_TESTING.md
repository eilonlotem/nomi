# Nomi UI Testing Guide

This document describes the UI testing flows for the Nomi dating app using Playwright.

## Test Environment Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- Backend server running on `http://localhost:8000`
- Frontend dev server running on `http://localhost:5173`

### Install Dependencies
```bash
cd frontend
npm install
npx playwright install
```

### Run Tests
```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e-flows.spec.js

# Run with UI mode (interactive)
npx playwright test --ui

# Run with headed browser (see browser)
npx playwright test --headed

# Run specific test by name
npx playwright test -g "login flow"
```

---

## Test Flows

### 1. Login Flow
**File:** `tests/login.spec.js`

**Steps:**
1. Navigate to the app root URL
2. Verify login page displays branding ("nomi", "Find Your Connection")
3. Click "Continue with Facebook" button
4. Verify navigation to language selection screen
5. Verify "Connected" status is shown

**Expected Result:** User is authenticated and shown language selection.

---

### 2. Match Flow (Swipe/Connect)
**File:** `tests/e2e-flows.spec.js`

**Steps:**
1. Complete login and onboarding
2. Navigate to Discovery view
3. View profile card (name, age, bio, tags)
4. Click "Connect" button (heart icon)
5. Verify match animation appears (if mutual like)
6. Verify match is added to matches list

**Expected Result:** Clicking connect either shows match animation (if mutual) or advances to next profile.

---

### 3. Send Message Flow
**File:** `tests/e2e-flows.spec.js`

**Steps:**
1. Navigate to matches view
2. Click on a match card or "Start Chat" button
3. Verify chat view opens with match's name
4. Type a message in the input field
5. Click "Send" button or press Enter
6. Verify message appears in the chat

**Expected Result:** Message is sent and displayed in the conversation.

---

### 4. Check Matches Flow
**File:** `tests/e2e-flows.spec.js`

**Steps:**
1. Complete login and navigate to Discovery
2. Click "My Matches" button (💬 icon in header)
3. Verify "My Matches" heading is displayed
4. Verify matches list shows match cards with:
   - Profile photo
   - Name and age
   - Bio snippet
   - "Start Chat" button

**Expected Result:** All matches are displayed with correct information.

---

### 5. Go to Existing Match and Send Message
**File:** `tests/e2e-flows.spec.js`

**Steps:**
1. Navigate to Matches view
2. Click on an existing match card
3. Verify chat view opens
4. Type a new message
5. Send the message
6. Verify message appears in conversation
7. Navigate back to matches
8. Verify match is still listed

**Expected Result:** Full conversation flow works end-to-end.

---

## Test File Structure

```
frontend/tests/
├── login.spec.js          # Login page tests
├── language-selection.spec.js  # Language selection tests
├── onboarding.spec.js     # Onboarding flow tests
├── preferences.spec.js    # Preferences screen tests
├── discovery.spec.js      # Discovery/swipe tests
├── profile.spec.js        # Profile editing tests
├── accessibility.spec.js  # A11y tests
├── rtl.spec.js           # RTL layout tests
└── e2e-flows.spec.js     # End-to-end user flows (NEW)
```

---

## Test Data Requirements

For tests to pass, the backend should have:
- Test users created via `python manage.py create_test_users`
- At least 2 matches created for the logged-in user
- Conversations created for matches

### Create Test Data
```bash
cd backend
source venv/bin/activate
python manage.py create_test_users --clear-existing
```

---

## Running Specific Test Suites

### Login Tests Only
```bash
npx playwright test tests/login.spec.js
```

### E2E Flow Tests Only
```bash
npx playwright test tests/e2e-flows.spec.js
```

### Run in Debug Mode
```bash
npx playwright test --debug
```

### Generate HTML Report
```bash
npx playwright test --reporter=html
npx playwright show-report
```

---

## CI/CD Integration

The tests are configured to:
- Run in headless mode on CI
- Retry failed tests 2 times
- Capture screenshots on failure
- Record video on failure
- Auto-start the dev server

### Environment Variables
- `TEST_URL`: Override the base URL (default: `http://localhost:5173`)
- `CI`: Set to `true` for CI environment behavior

---

## Troubleshooting

### Tests Timeout
- Ensure frontend dev server is running
- Ensure backend server is running
- Check network connectivity

### Login Fails
- Facebook SDK requires HTTPS in production
- Mock login is used in development (HTTP)

### Matches Not Showing
- Ensure test users are created
- Ensure matches exist in database
- Check API responses in browser console

### Element Not Found
- Check for correct role/name selectors
- Verify element is visible (not hidden by CSS)
- Wait for animations to complete
