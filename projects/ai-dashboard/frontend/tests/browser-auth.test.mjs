import assert from "node:assert/strict";
import { createRequire } from "node:module";
import path from "node:path";
import test from "node:test";

const require = createRequire(import.meta.url);
const {
  browserAuthConfigIsValid,
  browserAuthorizationIsValid,
  parseBasicAuthorization,
} = require(path.join(process.cwd(), ".auth-test", "browser-auth.js"));

const config = {
  username: "dashboard-admin",
  browserSecret: "browser-secret-that-is-longer-than-32-characters",
  backendToken: "backend-token-that-is-separate-and-over-32-characters",
};

function basic(username, password) {
  return `Basic ${Buffer.from(`${username}:${password}`, "utf8").toString("base64")}`;
}

test("requires strong distinct browser and backend credentials", () => {
  assert.equal(browserAuthConfigIsValid(config), true);
  assert.equal(browserAuthConfigIsValid({ ...config, browserSecret: "short" }), false);
  assert.equal(
    browserAuthConfigIsValid({ ...config, browserSecret: config.backendToken }),
    false,
  );
});

test("parses a valid Basic authorization value", () => {
  assert.deepEqual(parseBasicAuthorization(basic("admin", "secret:with-colon")), {
    username: "admin",
    password: "secret:with-colon",
  });
  assert.equal(parseBasicAuthorization("Bearer token"), null);
  assert.equal(parseBasicAuthorization("Basic not-base64!"), null);
});

test("accepts only the configured browser credential", async () => {
  assert.equal(
    await browserAuthorizationIsValid(
      basic(config.username, config.browserSecret),
      config,
    ),
    true,
  );
  assert.equal(
    await browserAuthorizationIsValid(basic(config.username, "wrong-secret"), config),
    false,
  );
  assert.equal(await browserAuthorizationIsValid(null, config), false);
});
