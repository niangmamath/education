/**
 * Talking to the API from the server, and never from the browser.
 *
 * The session cookie is `HttpOnly`, and it stays that way. If the browser called
 * the API directly it would be calling another origin, so the cookie would have
 * to be `SameSite=None; Secure` and travel as a third-party cookie — the exact
 * shape browsers are removing, and one that puts the session on the wire for
 * every script the page ever loads.
 *
 * So the browser only ever knows the web origin. Server components read the
 * cookie with `cookies()` and forward it to the API themselves; the one thing
 * the browser genuinely has to send — an xAPI statement relayed from the content
 * runtime — goes through a narrow route handler that does the same.
 *
 * Nothing here throws on a `401` or a `403`. A refusal is an answer: it means
 * "sign in again" or "not your space", and the caller decides what to show.
 */

import { cookies } from 'next/headers';

/**
 * A cross-service reference on Render (and platforms like it) gives a bare
 * `host:port` — a service on a private network isn't necessarily HTTP, so
 * there is no scheme to hand back. `fetch` needs a full URL, so a bare
 * address is completed here rather than asked of every deployment that
 * wires `API_URL` up to another service.
 */
function withScheme(url: string): string {
  return url.includes('://') ? url : `http://${url}`;
}

export const API_URL = withScheme(process.env.API_URL ?? 'http://localhost:8000');
const SESSION_COOKIE = process.env.SESSION_COOKIE_NAME ?? 'studentconnect_session';

export type ApiResult<T> =
  | { ok: true; status: number; data: T }
  | { ok: false; status: number; message: string };

type Options = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  /** Ticket minted by the API when a content is opened. Never in the body. */
  contentTicket?: string;
};

/** The session cookie this request carries, if the caller has one. */
export async function sessionCookie(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(SESSION_COOKIE)?.value;
}

/**
 * One call to the API, with the caller's session forwarded.
 *
 * `cache: 'no-store'` on every read, and deliberately: a dashboard that showed
 * yesterday's gaps would be worse than one that took an extra moment. Nothing
 * here is expensive enough to be worth a stale answer.
 */
export async function api<T>(path: string, options: Options = {}): Promise<ApiResult<T>> {
  const token = await sessionCookie();
  return call<T>(path, options, token);
}

/** The same call, with a session token the caller already holds. */
export async function apiWithToken<T>(
  path: string,
  token: string | undefined,
  options: Options = {},
): Promise<ApiResult<T>> {
  return call<T>(path, options, token);
}

async function call<T>(
  path: string,
  options: Options,
  token: string | undefined,
): Promise<ApiResult<T>> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (token) headers.Cookie = `${SESSION_COOKIE}=${token}`;
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';
  if (options.contentTicket) headers['X-Content-Ticket'] = options.contentTicket;

  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/v1${path}`, {
      method: options.method ?? 'GET',
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      cache: 'no-store',
    });
  } catch {
    // The API being unreachable is not the same as the API refusing, and the
    // pages say so differently: one is "come back later", the other is an answer.
    return { ok: false, status: 0, message: 'Le service est momentanément indisponible.' };
  }

  if (response.status === 204) {
    return { ok: true, status: 204, data: undefined as T };
  }

  const text = await response.text();
  let payload: unknown = undefined;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = undefined;
    }
  }

  if (!response.ok) {
    return { ok: false, status: response.status, message: messageOf(payload) };
  }
  return { ok: true, status: response.status, data: payload as T };
}

/**
 * The API's own French sentence, when it sent one.
 *
 * Its refusals are written to be shown — "Session invalide ou expirée", not a
 * code — so rewriting them here would lose the only wording anybody checked.
 */
function messageOf(payload: unknown): string {
  if (payload && typeof payload === 'object' && 'error' in payload) {
    const error = (payload as { error: unknown }).error;
    if (error && typeof error === 'object' && 'message' in error) {
      const message = (error as { message: unknown }).message;
      if (typeof message === 'string' && message) return message;
    }
  }
  return 'Cette action n’a pas pu être effectuée.';
}

export { SESSION_COOKIE };
