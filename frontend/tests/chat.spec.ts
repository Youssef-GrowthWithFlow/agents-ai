import { test, expect } from '@playwright/test';

/**
 * E2E tests for the chat interface
 *
 * Prerequisites:
 * - Backend must be running: cd backend && uvicorn main:app --reload
 * - Gemini API key must be configured in backend
 */

test.describe('Chat Interface', () => {
  test('should load the chat interface', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Check header (use role for better accessibility testing)
    await expect(page.getByRole('heading', { name: 'Growth With Flow Agent' })).toBeVisible();

    // Check welcome message
    await expect(page.getByText('How can I help you today?')).toBeVisible();

    // Check input is present
    await expect(page.getByPlaceholder('Enter a prompt here')).toBeVisible();
  });

  test('should send a message and receive a response', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Type a message
    const input = page.getByPlaceholder('Enter a prompt here');
    await input.fill('Hello, test message');

    // Wait for the API request when submitting
    const responsePromise = page.waitForResponse(response =>
      response.url().includes('/api/chat') && response.status() === 200
    );

    // Submit the form
    await page.locator('form').locator('button[type="submit"]').click();

    // Verify user message appears (using data-testid)
    const userMessage = page.getByTestId('user-message').filter({ hasText: 'Hello, test message' });
    await expect(userMessage).toBeVisible({ timeout: 10000 });

    // Wait for the API response
    await responsePromise;

    // Wait for agent response (using data-testid)
    const agentMessage = page.getByTestId('agent-message').first();
    await expect(agentMessage).toBeVisible({ timeout: 15000 });

    // Verify response is not empty
    await expect(agentMessage.locator('p')).not.toBeEmpty();
  });

  test('should clear input after sending message', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const input = page.getByPlaceholder('Enter a prompt here');
    await input.fill('Test message');
    await page.locator('form').locator('button[type="submit"]').click();

    // Input should be cleared
    await expect(input).toHaveValue('');
  });

  test('should disable submit button when input is empty', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const submitButton = page.locator('form').locator('button[type="submit"]');

    // Button should be disabled when input is empty
    await expect(submitButton).toBeDisabled();

    // Type something
    const input = page.getByPlaceholder('Enter a prompt here');
    await input.fill('Test');

    // Button should be enabled
    await expect(submitButton).toBeEnabled();

    // Clear input
    await input.clear();

    // Button should be disabled again
    await expect(submitButton).toBeDisabled();
  });
});
