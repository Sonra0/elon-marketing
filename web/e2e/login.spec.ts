import { test, expect } from "@playwright/test";

const FAKE_JWT =
  "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1IiwidGVuYW50X2lkIjoidCJ9.X-X-X";

test.beforeEach(async ({ page }) => {
  // Stub the FastAPI base for every spec.
  await page.route("**/tenants/me", async (route) => {
    await route.fulfill({ json: {
      user_id: "u", tenant_id: "t", role: "owner",
      telegram_linked: false, whatsapp_linked: false,
    }});
  });
  await page.route("**/admin/spend", async (route) => {
    await route.fulfill({ json: {
      tenant_id: "t", period_usd: 4.21, budget_usd: 50, pct_of_budget: 0.0842,
    }});
  });
  await page.route("**/admin/connectors", async (route) => {
    await route.fulfill({ json: [] });
  });
  await page.route("**/posts*", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ json: [] });
    } else {
      await route.fallback();
    }
  });
});

test("login page accepts a JWT and lands on dashboard", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator("h1")).toContainText("Log in");
  await page.fill("textarea", FAKE_JWT);
  await page.click("button:has-text('Continue')");
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Spend (this period)")).toBeVisible();
  await expect(page.getByText("$4.21")).toBeVisible();
});

test("dashboard shows empty connectors + recent posts", async ({ page, context }) => {
  await context.addInitScript((jwt) => {
    window.localStorage.setItem("elon_jwt", jwt);
  }, FAKE_JWT);
  await page.goto("/dashboard");
  await expect(page.getByText("None yet.")).toBeVisible();
  await expect(page.getByText("No posts yet.")).toBeVisible();
});
