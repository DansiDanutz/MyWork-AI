const test = require("node:test");
const assert = require("node:assert/strict");

const baseUrl = (process.env.TASK_TRACKER_BASE_URL || "http://localhost:3000").replace(
  /\/$/,
  "",
);

if (typeof fetch !== "function") {
  throw new Error(
    "Global fetch is not available. Use Node 18+ or set up a fetch polyfill.",
  );
}

async function fetchJson(path) {
  const response = await fetch(`${baseUrl}${path}`);
  const text = await response.text();
  let data = null;
  try {
    data = JSON.parse(text);
  } catch {
    // Keep data null if not JSON.
  }
  return { response, data, text };
}

test("root responds with HTML", async () => {
  const response = await fetch(`${baseUrl}/`, { redirect: "follow" });
  assert.ok(response.status < 500, `Unexpected status: ${response.status}`);
  const body = await response.text();
  assert.ok(body.trim().length > 0, "Empty body returned");
});

test("health endpoint returns JSON with status", async () => {
  const { response, data } = await fetchJson("/api/health");
  assert.ok([200, 503].includes(response.status));
  assert.ok(data, "Expected JSON response");
  assert.ok(["healthy", "unhealthy"].includes(data.status));
  assert.ok(data.checks, "Missing health checks");
});
