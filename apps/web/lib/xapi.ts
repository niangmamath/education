/**
 * H5P reports a whole exercise as one xAPI statement, and packs every
 * sub-answer into `result.response` joined by `[,]` — the separator the xAPI
 * "performance interaction" spec uses for a compound answer. Read verbatim,
 * "1[,]1[,]3[,]2[,]4[,]2[,]3[,]4" is not a sentence anyone can read; split on
 * the same separator and it is what it always was, a list of eight answers.
 */
export function readableResponse(text: string): string {
  return text.includes('[,]') ? text.split('[,]').join(', ') : text;
}
