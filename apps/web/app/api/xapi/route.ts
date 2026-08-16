/**
 * The one thing the browser genuinely has to send, and the narrowest door for it.
 *
 * A content runs on its own origin and hands its xAPI statements up with
 * `postMessage`. Only the browser is in a position to relay them, so this route
 * exists — and it is the only route handler in the app for that reason.
 *
 * It forwards, it does not decide. The session cookie is read here and never
 * leaves; the content ticket travels in a header because it is not part of the
 * statement; and the API is what says whether the statement is acceptable. This
 * file could not authorise anything if it wanted to: it holds no rule.
 *
 * The statement is passed through untouched. Rewriting it here would put a
 * second reading of the same event between the runtime and the record, and the
 * whole point of the API keeping the raw statement is that there is exactly one.
 */

import { NextResponse } from 'next/server';
import { apiWithToken, sessionCookie } from '../../../lib/api';

export async function POST(request: Request): Promise<NextResponse> {
  const token = await sessionCookie();
  if (!token) {
    return NextResponse.json({ received: false }, { status: 401 });
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ received: false }, { status: 400 });
  }

  if (!payload || typeof payload !== 'object') {
    return NextResponse.json({ received: false }, { status: 400 });
  }

  const { statement, ticket } = payload as { statement?: unknown; ticket?: unknown };
  if (!statement || typeof ticket !== 'string' || !ticket) {
    return NextResponse.json({ received: false }, { status: 400 });
  }

  const result = await apiWithToken('/me/xapi/statements', token, {
    method: 'POST',
    body: statement,
    contentTicket: ticket,
  });

  // The browser is told whether it was taken, and nothing else. A player has no
  // use for the reason, and a refusal that explained itself would explain itself
  // to whoever asked.
  return NextResponse.json({ received: result.ok }, { status: result.ok ? 202 : 400 });
}
