import type { ServerEvent } from './types';

const EVENT_NAMES = new Set(['meta', 'sources', 'token', 'refusal', 'done', 'error']);

/**
 * Parser SSE robusto sobre `ReadableStream`:
 * - eventos partidos entre chunks, separadores `\n\n` y `\r\n\r\n`,
 * - comentarios `: ping` ignorados, `data:` multilínea,
 * - UTF-8 multibyte partido (TextDecoder con `stream: true`).
 * Al cerrar el generador se cancela el lector (sin fugas).
 */
export async function* parseSseStream(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<ServerEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      buffer += decoder.decode(value, { stream: true });
      let separator = findSeparator(buffer);
      while (separator !== null) {
        const frame = buffer.slice(0, separator.index);
        buffer = buffer.slice(separator.index + separator.length);
        const event = parseFrame(frame);
        if (event !== null) {
          yield event;
        }
        separator = findSeparator(buffer);
      }
    }
    buffer += decoder.decode();
    const event = parseFrame(buffer);
    if (event !== null) {
      yield event;
    }
  } finally {
    try {
      await reader.cancel();
    } catch {
      // el stream ya estaba cancelado
    }
    reader.releaseLock();
  }
}

function findSeparator(buffer: string): { index: number; length: number } | null {
  const lf = buffer.indexOf('\n\n');
  const crlf = buffer.indexOf('\r\n\r\n');
  if (lf === -1 && crlf === -1) {
    return null;
  }
  if (crlf !== -1 && (lf === -1 || crlf < lf)) {
    return { index: crlf, length: 4 };
  }
  return { index: lf, length: 2 };
}

function parseFrame(frame: string): ServerEvent | null {
  let eventName = '';
  const dataLines: string[] = [];

  for (const rawLine of frame.split(/\r?\n/)) {
    if (rawLine === '' || rawLine.startsWith(':')) {
      continue;
    }
    const colon = rawLine.indexOf(':');
    const field = colon === -1 ? rawLine : rawLine.slice(0, colon);
    let value = colon === -1 ? '' : rawLine.slice(colon + 1);
    if (value.startsWith(' ')) {
      value = value.slice(1);
    }
    if (field === 'event') {
      eventName = value;
    } else if (field === 'data') {
      dataLines.push(value);
    }
  }

  if (!EVENT_NAMES.has(eventName) || dataLines.length === 0) {
    return null;
  }
  try {
    const data: unknown = JSON.parse(dataLines.join('\n'));
    return { event: eventName, data } as ServerEvent;
  } catch {
    return null;
  }
}
