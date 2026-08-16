'use server';

/**
 * Everything the browser can cause to happen, and nothing it can do directly.
 *
 * These run on the server. The form posts to Next, Next calls the API with the
 * session cookie, and the browser never holds a credential or an API address.
 * A server action is also the only place that may set a cookie on this origin,
 * which is what signing in needs: the API mints the session, and this relays it.
 *
 * Every action returns a message rather than throwing. A refusal from the API is
 * an answer meant to be shown — "Identifiants invalides", "Cette activité n’est
 * plus ouverte" — and turning it into a stack trace would lose the only wording
 * anyone reviewed.
 */

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { SESSION_COOKIE, apiWithToken } from './api';
import type { AppliedRemediation, Attempt, ChildAssignment } from './types';

const API_URL = process.env.API_URL ?? 'http://localhost:8000';

export type FormState = { error: string | null };

/**
 * Sign in, and put the API's session on this origin.
 *
 * The cookie is re-set here rather than relayed verbatim: the API set it for its
 * own host, and a `Set-Cookie` copied across would either be dropped or land on
 * the wrong domain. Its flags are re-stated, `httpOnly` included, so nothing
 * about the session becomes readable by moving it.
 */
async function signIn(path: string, payload: unknown): Promise<string | null> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/v1${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      cache: 'no-store',
    });
  } catch {
    return 'Le service est momentanément indisponible.';
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message =
      body && typeof body === 'object' && 'error' in body
        ? ((body as { error: { message?: string } }).error?.message ?? null)
        : null;
    return message ?? 'La connexion a échoué.';
  }

  const token = readSessionToken(response.headers.getSetCookie());
  if (!token) return 'La session n’a pas pu être ouverte.';

  const store = await cookies();
  store.set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
  });
  return null;
}

function readSessionToken(setCookies: string[]): string | null {
  for (const header of setCookies) {
    const [pair] = header.split(';');
    const separator = pair.indexOf('=');
    if (separator > 0 && pair.slice(0, separator).trim() === SESSION_COOKIE) {
      return pair.slice(separator + 1);
    }
  }
  return null;
}

export async function loginParent(_: FormState, formData: FormData): Promise<FormState> {
  const error = await signIn('/auth/parent/login', {
    email: String(formData.get('email') ?? ''),
    password: String(formData.get('password') ?? ''),
  });
  if (error) return { error };
  redirect('/parent');
}

export async function loginChild(_: FormState, formData: FormData): Promise<FormState> {
  const error = await signIn('/auth/child/login', {
    family_code: String(formData.get('family_code') ?? ''),
    pseudonym: String(formData.get('pseudonym') ?? ''),
    pin: String(formData.get('pin') ?? ''),
  });
  if (error) return { error };
  redirect('/eleve');
}

/**
 * Sign out, on both sides.
 *
 * The API is told first so the session leaves Redis; the cookie is cleared even
 * if that call fails, because a cookie nobody can use is better than a signed-in
 * look with nothing behind it.
 */
export async function logout(): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  if (token) {
    await apiWithToken('/auth/logout', token, { method: 'POST' }).catch(() => null);
  }
  store.delete(SESSION_COOKIE);
  redirect('/');
}

/**
 * Take up an activity, and open the attempt that will hold what happens in it.
 *
 * Both in one act, because the page that follows needs the attempt to exist: a
 * statement from the content runtime is refused when no attempt is running, and
 * a child who reached the player only to be told to press something else would
 * be paying for an ordering we chose.
 *
 * Both are idempotent on the API's side — starting twice returns the same
 * attempt, by a partial unique index rather than by a check — so a double tap on
 * a slow connection costs nothing. That is exactly the case a child on a
 * household tablet is most likely to produce.
 */
export async function startActivity(assignmentId: string): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  await apiWithToken<ChildAssignment>(`/me/activities/${assignmentId}/start`, token, {
    method: 'POST',
  });
  await apiWithToken<Attempt>(`/me/activities/${assignmentId}/attempts`, token, {
    method: 'POST',
  });
  revalidatePath('/eleve');
  revalidatePath('/eleve/activites');
  redirect(`/eleve/activites/${assignmentId}`);
}

/**
 * Finish the attempt under way, which also finishes the activity.
 *
 * Nothing is assigned as a consequence: the platform proposes and a parent
 * gives. What changes here is only what the child did.
 */
export async function finishAttempt(assignmentId: string, attemptId: string): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  await apiWithToken<Attempt>(`/me/attempts/${attemptId}/complete`, token, {
    method: 'POST',
  });
  revalidatePath('/eleve');
  revalidatePath('/eleve/progression');
  redirect(`/eleve/activites/${assignmentId}/resultat`);
}

/**
 * Give the activities the platform proposes for one child.
 *
 * The parent's act: the button removes the retyping, not the decision.
 */
export async function applyRemediation(childId: string): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  await apiWithToken<AppliedRemediation>(`/children/${childId}/remediation`, token, {
    method: 'POST',
  });
  revalidatePath(`/parent/enfants/${childId}`);
  revalidatePath('/parent');
}
