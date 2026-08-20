/**
 * One place that turns an ISO timestamp into what a parent or a child reads.
 *
 * `fr-FR` throughout: the platform has one audience and one locale, and a date
 * formatted three different ways across three pages would read as three
 * different platforms.
 */
const FORMATTER = new Intl.DateTimeFormat('fr-FR', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

export function formatDateTime(iso: string): string {
  return FORMATTER.format(new Date(iso));
}
