import { test, expect } from "@playwright/test";

const FAKE_JWT = "eyJhbGciOiJIUzI1NiJ9.payload.sig";

test("drafts page shows pending and lets you approve", async ({ page, context }) => {
  await context.addInitScript((jwt) => {
    window.localStorage.setItem("elon_jwt", jwt);
  }, FAKE_JWT);

  let approved = false;
  await page.route("**/posts**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();
    if (method === "GET" && url.endsWith("/posts")) {
      await route.fulfill({ json: [{
        id: "p1", platform: "tiktok", state: "review",
        idea: "Trend: rapid product unboxing",
        hook: "What I packed for the move (it's not what you think)",
        caption: "Five things I never travel without — surprises start at #3.",
        cta: "Save this for your next trip.",
        score_json: { impact: 70, effort: 30, risk: 10 },
        requires_human_review: false,
        scheduled_at: null, published_at: null, external_post_id: null,
        created_at: "2026-04-28T09:00:00Z",
      }]});
    } else if (method === "POST" && url.includes("/p1/decide")) {
      approved = true;
      await route.fulfill({ json: {
        id: "p1", platform: "tiktok", state: "approved",
        idea: "x", hook: "y", caption: "z", cta: "",
        score_json: {}, requires_human_review: false,
        scheduled_at: null, published_at: null, external_post_id: null,
        created_at: "2026-04-28T09:00:00Z",
      }});
    } else {
      await route.fulfill({ json: [] });
    }
  });

  await page.goto("/drafts");
  await expect(page.getByText("Trend: rapid product unboxing")).toBeVisible();
  // TikTok-specific approve label per locked decision.
  await page.click("button:has-text('Approve TikTok post')");
  await page.waitForTimeout(200);
  expect(approved).toBe(true);
});
