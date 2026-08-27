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
import { API_URL, SESSION_COOKIE, apiWithToken } from './api';
import type {
  AnswerFeedback,
  AppliedRemediation,
  Attempt,
  ChildAssignment,
} from './types';

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

/**
 * Open a parent account.
 *
 * Registering does not sign anyone in, and that is the API's decision rather
 * than an oversight: ADR-005 places email verification between the two. So this
 * creates the account and hands the visitor to the sign-in form, where the
 * password they just chose is the one that works.
 */
export async function registerParent(
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const password = String(formData.get('password') ?? '');
  if (password.length < 12) {
    return { error: 'Le mot de passe doit faire au moins 12 caractères.' };
  }
  if (password !== String(formData.get('password_confirm') ?? '')) {
    return { error: 'Les deux mots de passe ne sont pas identiques.' };
  }

  const created = await call('/auth/parent/register', {
    email: String(formData.get('email') ?? ''),
    password,
    display_name: String(formData.get('display_name') ?? ''),
  });
  if (created !== null) return { error: created };

  redirect('/connexion?cree=1');
}

/**
 * Open a child profile from the family code, without an adult present.
 *
 * The profile waits: a family code alone must never be enough to join a family,
 * only to ask to. A parent activates it, and until then it cannot sign in — so
 * this page tells the child exactly that rather than letting her discover it at
 * her first attempt.
 */
export async function registerChild(
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const pin = String(formData.get('pin') ?? '');
  if (!/^[0-9]{6}$/.test(pin)) {
    return { error: 'Le code secret doit être six chiffres.' };
  }

  const created = await call('/auth/child/register', {
    family_code: String(formData.get('family_code') ?? '').trim(),
    level_code: String(formData.get('level_code') ?? '').trim(),
    pseudonym: String(formData.get('pseudonym') ?? '').trim(),
    pin,
    display_name: String(formData.get('display_name') ?? '').trim(),
  });
  if (created !== null) return { error: created };

  redirect('/connexion/eleve?demande=1');
}

/**
 * Add a child profile from the parent's own space, usable straight away.
 *
 * No waiting here, unlike the child's own registration: the adult who owns the
 * family is the one asking, so there is nobody left to approve it.
 */
export async function createChild(_: FormState, formData: FormData): Promise<FormState> {
  const pin = String(formData.get('pin') ?? '');
  if (!/^[0-9]{6}$/.test(pin)) {
    return { error: 'Le code secret doit être six chiffres.' };
  }

  const store = await cookies();
  const created = await apiWithToken('/auth/children', store.get(SESSION_COOKIE)?.value, {
    method: 'POST',
    body: {
      pseudonym: String(formData.get('pseudonym') ?? '').trim(),
      level_code: String(formData.get('level_code') ?? '').trim(),
      pin,
      display_name: String(formData.get('display_name') ?? '').trim(),
    },
  });
  if (!created.ok) return { error: created.message };

  revalidatePath('/parent/enfants');
  revalidatePath('/parent');
  return { error: null };
}

/** Open or close access to a profile. The assessment is given on the first open. */
export async function setChildAccess(childId: string, open: boolean): Promise<void> {
  const store = await cookies();
  await apiWithToken(
    `/auth/children/${childId}/${open ? 'activate' : 'deactivate'}`,
    store.get(SESSION_COOKIE)?.value,
    { method: 'POST' },
  );
  revalidatePath('/parent/enfants');
  revalidatePath('/parent');
}

/** One unauthenticated call, returning the API's own sentence when it refuses. */
async function call(path: string, payload: unknown): Promise<string | null> {
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
  if (response.ok) return null;

  const body = await response.json().catch(() => null);
  if (body && typeof body === 'object' && 'error' in body) {
    const message = (body as { error: { message?: string } }).error?.message;
    if (message) return message;
  }
  if (response.status === 422) {
    return 'Certaines informations ne sont pas valides ; vérifiez le formulaire.';
  }
  return 'Le compte n’a pas pu être créé.';
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
 *
 * `destination` is bound at each `SignOutButton`, never guessed here: by the
 * time this runs the cookie is already gone, so re-asking the API "which space
 * was this" would be asking a session that no longer answers. The caller
 * already knows which header it is.
 */
export async function logout(destination: string): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  if (token) {
    await apiWithToken('/auth/logout', token, { method: 'POST' }).catch(() => null);
  }
  store.delete(SESSION_COOKIE);
  redirect(destination);
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
 * Sit the initiation assessment: start it, answer it, finish it.
 *
 * One submission for the whole thing rather than one request per question. A
 * child answering on a household tablet should not lose her place to a flaky
 * connection halfway through, and the platform records nothing until she says
 * she has finished — which is the same promise the rest of the Élève space makes.
 *
 * The answers are positions in a list of choices. Whether each is right is
 * decided by the server, from its own copy: the browser is never told, and could
 * not be believed if it said.
 */
export async function submitAssessment(
  assignmentId: string,
  formData: FormData,
): Promise<void> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;

  await apiWithToken(`/me/activities/${assignmentId}/start`, token, { method: 'POST' });
  const attempt = await apiWithToken<Attempt>(
    `/me/activities/${assignmentId}/attempts`,
    token,
    { method: 'POST' },
  );
  if (!attempt.ok) return;

  for (const [name, value] of formData.entries()) {
    if (!name.startsWith('q:')) continue;
    const chosen = Number(value);
    if (!Number.isInteger(chosen)) continue;
    await apiWithToken(`/me/assessment/attempts/${attempt.data.id}/answers`, token, {
      method: 'POST',
      body: { question_ref: name.slice(2), chosen_index: chosen },
    });
  }

  await apiWithToken(`/me/attempts/${attempt.data.id}/complete`, token, {
    method: 'POST',
  });
  revalidatePath('/eleve');
  revalidatePath('/eleve/progression');
  redirect(`/eleve/activites/${assignmentId}/resultat`);
}

/**
 * Répondre à une question d'une fiche, et rapporter ce qu'elle dit.
 *
 * Une action serveur plutôt qu'un appel depuis le navigateur, parce que
 * `API_URL` ne quitte jamais le serveur (ADR-016) — mais une action par
 * question, et non un envoi unique à la fin comme pour l'examen. La différence
 * est le sujet même de la fiche : elle explique au fur et à mesure, sinon elle
 * n'apprend rien et redevient un contrôle.
 *
 * L'appelant reçoit `null` en cas d'échec plutôt qu'une exception : une réponse
 * perdue ne doit pas faire disparaître la fiche sous les yeux d'une enfant.
 */
export async function answerFicheQuestion(
  attemptId: string,
  questionRef: string,
  chosenIndex: number,
): Promise<AnswerFeedback | null> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;

  const said = await apiWithToken<AnswerFeedback>(
    `/me/fiches/attempts/${attemptId}/answers`,
    token,
    { method: 'POST', body: { question_ref: questionRef, chosen_index: chosenIndex } },
  );

  return said.ok ? said.data : null;
}

/**
 * Faire passer un enfant dans la classe supérieure.
 *
 * Le geste appartient au parent : la plateforme ne connaît ni l'école de
 * l'enfant, ni son année scolaire, ni ce qu'un conseil de maîtres a décidé.
 * Elle enregistre la décision, déplace le palier de compétences, et donne
 * l'examen d'entrée de la nouvelle classe.
 *
 * Rien n'est effacé : les lectures des classes antérieures restent, et le
 * diagnostic continue d'y descendre.
 *
 * **Le refus est rendu, pas avalé.** La première version jetait la réponse de
 * l'API : quand elle refusait, le bouton semblait ne rien faire du tout, et un
 * parent n'avait aucun moyen de savoir si le geste avait échoué ou si la page
 * n'avait pas fini de se recharger. Un bouton muet est pire qu'un bouton absent.
 */
export async function promoteChild(
  childId: string,
  // Les deux arguments que `useActionState` impose : l'état précédent et le
  // formulaire. Le passage n'a rien à y lire — il n'a qu'un enfant et une
  // direction — mais la signature doit être celle que React appelle.
  _previous: FormState,
  _formData: FormData,
): Promise<FormState> {
  const store = await cookies();
  const done = await apiWithToken(
    `/auth/children/${childId}/promotion`,
    store.get(SESSION_COOKIE)?.value,
    { method: 'POST' },
  );

  if (!done.ok) {
    return { error: done.message };
  }

  revalidatePath(`/parent/enfants/${childId}`);
  revalidatePath('/parent/enfants');
  revalidatePath('/parent');
  return { error: null };
}

/**
 * Déclarer ou corriger la classe d'un enfant.
 *
 * Deux cas réels : un profil ouvert avant que la plateforme ne demande la
 * classe n'en a pas et ne reçoit donc aucun examen ; et un parent se trompe à
 * l'inscription. Les deux se rattrapent sans recréer le profil et sans perdre
 * son historique.
 */
export async function setChildLevel(
  childId: string,
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const store = await cookies();
  const chosen = String(formData.get('level_code') ?? '').trim();

  if (!chosen) {
    return { error: 'Choisissez une classe avant d’enregistrer.' };
  }

  const done = await apiWithToken(
    `/auth/children/${childId}/level`,
    store.get(SESSION_COOKIE)?.value,
    { method: 'PUT', body: { level_code: chosen } },
  );

  if (!done.ok) {
    return { error: done.message };
  }

  revalidatePath(`/parent/enfants/${childId}`);
  revalidatePath('/parent/enfants');
  revalidatePath('/parent');
  return { error: null };
}

export async function updateParentProfile(
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const store = await cookies();
  const displayName = String(formData.get('display_name') ?? '').trim();

  if (!displayName) {
    return { error: 'Le nom ne peut pas être vide.' };
  }

  const done = await apiWithToken('/auth/me', store.get(SESSION_COOKIE)?.value, {
    method: 'PUT',
    body: { display_name: displayName },
  });

  if (!done.ok) {
    return { error: done.message };
  }

  revalidatePath('/parent', 'layout');
  return { error: null };
}

export async function changeParentPassword(
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const store = await cookies();
  const currentPassword = String(formData.get('current_password') ?? '');
  const newPassword = String(formData.get('new_password') ?? '');
  const confirmPassword = String(formData.get('confirm_password') ?? '');

  if (newPassword !== confirmPassword) {
    return { error: 'Les deux mots de passe ne correspondent pas.' };
  }

  const done = await apiWithToken('/auth/me/password', store.get(SESSION_COOKIE)?.value, {
    method: 'PUT',
    body: { current_password: currentPassword, new_password: newPassword },
  });

  if (!done.ok) {
    return { error: done.message };
  }

  return { error: null };
}

export async function updateChildName(
  childId: string,
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const store = await cookies();
  const displayName = String(formData.get('display_name') ?? '').trim();

  if (!displayName) {
    return { error: 'Le nom ne peut pas être vide.' };
  }

  const done = await apiWithToken(
    `/auth/children/${childId}`,
    store.get(SESSION_COOKIE)?.value,
    { method: 'PUT', body: { display_name: displayName } },
  );

  if (!done.ok) {
    return { error: done.message };
  }

  revalidatePath(`/parent/enfants/${childId}`);
  revalidatePath('/parent/enfants');
  revalidatePath('/parent');
  return { error: null };
}

export async function resetChildPin(
  childId: string,
  _: FormState,
  formData: FormData,
): Promise<FormState> {
  const store = await cookies();
  const pin = String(formData.get('pin') ?? '');

  const done = await apiWithToken(
    `/auth/children/${childId}/pin`,
    store.get(SESSION_COOKIE)?.value,
    { method: 'PUT', body: { pin } },
  );

  if (!done.ok) {
    return { error: done.message };
  }

  return { error: null };
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
