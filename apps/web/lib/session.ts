/**
 * Who is signed in, and what a page does when nobody is.
 *
 * The guard runs in the layout of each space rather than in a middleware. A
 * middleware would decide from the cookie's presence alone, which says nothing:
 * a cookie whose session Redis no longer holds looks exactly like a valid one.
 * Asking the API is the only way to know, and it is the API that decides — the
 * web never interprets a session for itself.
 *
 * A wrong-space session is sent back to its own space rather than to the sign-in
 * page: a child who lands on a Parent URL is not signed out, she is elsewhere.
 */

import { redirect } from 'next/navigation';
import { api } from './api';
import type { Session } from './types';

export async function currentSession(): Promise<Session | null> {
  const result = await api<Session>('/auth/session');
  return result.ok ? result.data : null;
}

export async function requireParent(): Promise<Session> {
  const session = await currentSession();
  if (!session) redirect('/connexion');
  if (session.user_type !== 'parent') redirect('/eleve');
  return session;
}

export async function requireChild(): Promise<Session> {
  const session = await currentSession();
  if (!session) redirect('/connexion/eleve');
  if (session.user_type !== 'child') redirect('/parent');
  return session;
}
