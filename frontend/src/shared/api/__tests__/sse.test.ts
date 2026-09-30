import { afterEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '../client';
import { streamChat } from '../chatStream';
import { parseSseStream } from '../sse';
import type { ServerEvent } from '../types';

const encoder = new TextEncoder();

function streamFrom(chunks: (string | Uint8Array)[]): ReadableStream<Uint8Array> {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(typeof chunk === 'string' ? encoder.encode(chunk) : chunk);
      }
      controller.close();
    },
  });
}

async function collect(stream: ReadableStream<Uint8Array>): Promise<ServerEvent[]> {
  const events: ServerEvent[] = [];
  for await (const event of parseSseStream(stream)) {
    events.push(event);
  }
  return events;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('parseSseStream', () => {
  it('parsea eventos partidos entre chunks', async () => {
    const events = await collect(
      streamFrom([
        'event: meta\ndata: {"message_id":"m1","prompt_version":"v1","tier":"gpu"}\n\n',
        'event: tok',
        'en\ndata: {"t":"Ho',
        'la"}\n\n',
        'event: done\ndata: {"first_token_ms":12,"total_ms":30}\n\n',
      ]),
    );

    expect(events.map((event) => event.event)).toEqual(['meta', 'token', 'done']);
    expect(events[1]).toEqual({ event: 'token', data: { t: 'Hola' } });
  });

  it('soporta \\r\\n y ignora comentarios ping', async () => {
    const events = await collect(
      streamFrom([': ping\r\n\r\n', 'event: token\r\ndata: {"t":"x"}\r\n\r\n', ': ping\n\n']),
    );

    expect(events).toEqual([{ event: 'token', data: { t: 'x' } }]);
  });

  it('no rompe con UTF-8 multibyte partido', async () => {
    const frame = encoder.encode('event: token\ndata: {"t":"á"}\n\n');
    const splitAt = frame.indexOf(0xc3) + 1;

    const events = await collect(streamFrom([frame.slice(0, splitAt), frame.slice(splitAt)]));

    expect(events).toEqual([{ event: 'token', data: { t: 'á' } }]);
  });

  it('parsea eventos de error con código', async () => {
    const events = await collect(
      streamFrom([
        'event: error\ndata: {"code":"output_blocked","message":"bloqueado","retry_after_s":null}\n\n',
      ]),
    );

    expect(events[0]).toEqual({
      event: 'error',
      data: { code: 'output_blocked', message: 'bloqueado', retry_after_s: null },
    });
  });

  it('ignora eventos desconocidos y JSON corrupto', async () => {
    const events = await collect(
      streamFrom([
        'event: desconocido\ndata: {"x":1}\n\n',
        'event: token\ndata: no-es-json\n\n',
        'event: token\ndata: {"t":"ok"}\n\n',
      ]),
    );

    expect(events).toEqual([{ event: 'token', data: { t: 'ok' } }]);
  });

  it('cancela el lector al cerrar el generador', async () => {
    let cancelled = false;
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('event: token\ndata: {"t":"a"}\n\n'));
      },
      cancel() {
        cancelled = true;
      },
    });

    const generator = parseSseStream(stream);
    const first = await generator.next();
    expect(first.value).toEqual({ event: 'token', data: { t: 'a' } });
    await generator.return(undefined);

    expect(cancelled).toBe(true);
  });
});

describe('streamChat', () => {
  it('entrega los eventos y no reconecta', async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(
          streamFrom([
            'event: token\ndata: {"t":"Hola"}\n\n',
            'event: done\ndata: {"first_token_ms":1,"total_ms":2}\n\n',
          ]),
          { status: 200 },
        ),
    );
    vi.stubGlobal('fetch', fetchMock);
    const received: ServerEvent[] = [];

    await streamChat({ message: 'hola' }, { onEvent: (event) => received.push(event) });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(received.map((event) => event.event)).toEqual(['token', 'done']);
  });

  it('lanza ApiError con código y retry_after en respuestas no-ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(JSON.stringify({ code: 'rate_limited', retry_after_s: 42 }), {
            status: 429,
          }),
      ),
    );

    const promise = streamChat({ message: 'hola' }, { onEvent: () => undefined });

    await expect(promise).rejects.toThrowError(ApiError);
    await promise.catch((error: unknown) => {
      expect((error as ApiError).code).toBe('rate_limited');
      expect((error as ApiError).retryAfter).toBe(42);
    });
  });

  it('propaga el abort del cliente', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new DOMException('aborted', 'AbortError');
      }),
    );

    await expect(streamChat({ message: 'hola' }, { onEvent: () => undefined })).rejects.toThrow(
      'aborted',
    );
  });
});
