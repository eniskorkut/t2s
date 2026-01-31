import { test, expect } from '@playwright/test';

test.describe('Chat Integration Flow', () => {
    const TEST_EMAIL = 'admin@example.com';
    const TEST_PASSWORD = 'password'; // Ensure this matches a valid user or seed data

    test('should login and receive chat response', async ({ page }) => {
        // 1. Go to Login Page
        await page.goto('/login');

        // 2. Fill Credentials
        await page.fill('input[type="email"]', TEST_EMAIL);
        await page.fill('input[type="password"]', TEST_PASSWORD);

        // 3. Submit
        await page.click('button[type="submit"]');

        // 4. Verify Redirect to Home
        await expect(page).toHaveURL('/');

        // 5. Verify Sidebar/Header (indicates successful auth)
        await expect(page.locator('text=Yeni Sohbet')).toBeVisible();

        // 6. Send a Message
        const messageInput = page.locator('textarea[placeholder="Herhangi bir şey sor"]');
        await messageInput.fill('Satışları getir');
        await messageInput.press('Enter');

        // 7. Verify Response
        // Wait for assistant message to appear (skeleton handled by 'text=...')
        // Look for SQL code block or specific text that indicates success.
        // Assuming backend returns some SQL or explanation.
        await expect(page.locator('.prose')).toContainText('SELECT', { timeout: 15000 });
    });
});
