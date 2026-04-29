import { test, expect } from "@playwright/test";

const FAKE_JWT = "eyJhbGciOiJIUzI1NiJ9.payload.sig";

test("brand page renders current memory and queues ingest", async ({ page, context }) => {
  await context.addInitScript((jwt) => {
    window.localStorage.setItem("elon_jwt", jwt);
  }, FAKE_JWT);

  let ingested = false;
  await page.route("**/posts/_brand", async (route) => {
    await route.fulfill({ json: {
      version: 1,
      voice_json: { tone: ["calm", "concrete"] },
      visual_json: { palette: ["#111", "#eee"] },
      offering_json: { category: "DTC" },
      audience_json: { personas: [] },
      positioning_json: { oneliner: "Less stuff, more substance." },
      pillars_json: [{ id: "p1", name: "Craft", description: "How it's made" }],
      forbidden_json: { words: [] },
    }});
  });
  await page.route("**/agent/ingest", async (route) => {
    ingested = true;
    await route.fulfill({ json: { task_id: "task-123" } });
  });

  await page.goto("/brand");
  await expect(page.getByText("v1")).toBeVisible();
  await expect(page.getByText("Less stuff, more substance.")).toBeVisible();

  await page.fill("input[placeholder*='https://']", "https://example.com");
  await page.click("button:has-text('Ingest')");
  await page.waitForTimeout(200);
  expect(ingested).toBe(true);
});
