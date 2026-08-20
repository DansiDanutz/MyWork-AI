const MINIMUM_SECRET_LENGTH = 32;

export interface BrowserAuthConfig {
  username: string;
  browserSecret: string;
  backendToken: string;
}

export function browserAuthConfigIsValid(config: BrowserAuthConfig): boolean {
  return (
    config.username.trim().length > 0 &&
    config.browserSecret.length >= MINIMUM_SECRET_LENGTH &&
    config.backendToken.length >= MINIMUM_SECRET_LENGTH &&
    config.browserSecret !== config.backendToken
  );
}

export function parseBasicAuthorization(
  authorization: string | null,
): { username: string; password: string } | null {
  if (!authorization?.startsWith("Basic ")) return null;

  try {
    const encoded = authorization.slice("Basic ".length).trim();
    if (!encoded) return null;

    const binary = atob(encoded);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    const decoded = new TextDecoder().decode(bytes);
    const separator = decoded.indexOf(":");
    if (separator < 1) return null;

    return {
      username: decoded.slice(0, separator),
      password: decoded.slice(separator + 1),
    };
  } catch {
    return null;
  }
}

async function digest(value: string): Promise<Uint8Array> {
  const bytes = new TextEncoder().encode(value);
  return new Uint8Array(await globalThis.crypto.subtle.digest("SHA-256", bytes));
}

async function valuesMatch(left: string, right: string): Promise<boolean> {
  const [leftDigest, rightDigest] = await Promise.all([digest(left), digest(right)]);
  let difference = 0;
  for (let index = 0; index < leftDigest.length; index += 1) {
    difference |= leftDigest[index] ^ rightDigest[index];
  }
  return difference === 0;
}

export async function browserAuthorizationIsValid(
  authorization: string | null,
  config: BrowserAuthConfig,
): Promise<boolean> {
  if (!browserAuthConfigIsValid(config)) return false;
  const credentials = parseBasicAuthorization(authorization);
  if (!credentials) return false;

  const [usernameMatches, passwordMatches] = await Promise.all([
    valuesMatch(credentials.username, config.username),
    valuesMatch(credentials.password, config.browserSecret),
  ]);
  return usernameMatches && passwordMatches;
}
