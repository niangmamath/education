'use client';

import { useEffect, useMemo, useState } from 'react';

/**
 * The content, in its own frame, and the bridge that carries what it says.
 *
 * This is the piece the platform has been missing since the runtime was built:
 * `play.html` has been raising xAPI statements to its parent window all along,
 * with nobody listening. Here is the listener.
 *
 * **Every message is checked against the content origin before it is read.**
 * `postMessage` delivers to a window, not to a sender: any frame, any opener,
 * any extension can post into this page. Without the origin check, anything on
 * the machine could file answers in a child's name. The origin is taken from the
 * play URL the API returned, so it cannot be pointed elsewhere by a query string.
 *
 * The statement is forwarded exactly as it arrived. The server sets where it
 * came from and which attempt it belongs to; this file does not get to say.
 */

type Status = 'loading' | 'ready' | 'error';

export function ContentPlayer({ playUrl }: { playUrl: string }) {
  const [reported, setReported] = useState<Status | null>(null);
  const [sent, setSent] = useState(0);

  // Derived during render rather than in the effect: the origin and the ticket
  // are a reading of the prop, and computing them in an effect would mean one
  // render where the page does not yet know which origin it trusts.
  const source = useMemo(() => {
    try {
      const url = new URL(playUrl);
      return { origin: url.origin, ticket: url.searchParams.get('t') ?? '' };
    } catch {
      return null;
    }
  }, [playUrl]);

  const status: Status = source === null ? 'error' : (reported ?? 'loading');

  useEffect(() => {
    if (source === null) return;
    const { origin, ticket } = source;

    function onMessage(event: MessageEvent) {
      // The check that makes the rest of this function safe.
      if (event.origin !== origin) return;

      const data = event.data as { type?: string; statement?: unknown } | null;
      if (!data || typeof data !== 'object') return;

      if (data.type === 'studentconnect:ready') {
        setReported('ready');
        return;
      }
      if (data.type === 'studentconnect:error') {
        setReported('error');
        return;
      }
      if (data.type !== 'studentconnect:xapi' || !data.statement) return;

      void fetch('/api/xapi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ statement: data.statement, ticket }),
      })
        .then((response) => {
          if (response.ok) setSent((count) => count + 1);
        })
        .catch(() => {
          // A statement that does not reach the server is not worth interrupting
          // a child over: what she answered is still hers to redo, and the
          // declared path records the attempt either way.
        });
    }

    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, [source]);

  return (
    <div>
      {status === 'loading' ? (
        <p className="text-secondary" role="status">
          Chargement de l’activité…
        </p>
      ) : null}
      {status === 'error' ? (
        <div className="alert alert-warning" role="alert">
          Cette activité n’a pas pu s’ouvrir. Tu peux réessayer plus tard.
        </div>
      ) : null}

      <iframe
        src={playUrl}
        title="Activité"
        className="w-100 border rounded"
        style={{ minHeight: '32rem' }}
        // The runtime is already isolated by its own origin; the sandbox is the
        // second lock, and it grants exactly what a H5P content needs to run.
        sandbox="allow-scripts allow-same-origin"
        allow=""
      />

      <p className="small text-secondary mt-2" aria-live="polite">
        {sent > 0
          ? `${sent} réponse${sent > 1 ? 's enregistrées' : ' enregistrée'}.`
          : 'Tes réponses sont enregistrées au fur et à mesure.'}
      </p>
    </div>
  );
}
