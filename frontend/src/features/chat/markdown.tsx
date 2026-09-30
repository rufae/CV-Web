import type { ReactNode } from 'react';

const INLINE_PATTERN = /(\[[^\]]+\]\((https?:\/\/[^\s)]+)\))|(\*\*[^*]+\*\*)|(\[\d+\])/g;

/** Renderiza inline: enlaces http(s) seguros, negritas y citas [n]. */
export function renderInline(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const pattern = new RegExp(INLINE_PATTERN);
  let lastIndex = 0;
  let match = pattern.exec(text);
  while (match !== null) {
    if (match.index > lastIndex) {
      nodes.push(text.slice(lastIndex, match.index));
    }
    const [full, link, href, bold, citation] = match;
    const key = `${keyPrefix}-${match.index}`;
    if (link !== undefined && href !== undefined) {
      nodes.push(
        <a
          key={key}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent underline"
        >
          {link}
        </a>,
      );
    } else if (bold !== undefined) {
      nodes.push(<strong key={key}>{bold.slice(2, -2)}</strong>);
    } else if (citation !== undefined) {
      nodes.push(
        <sup key={key} className="text-accent">
          {citation.slice(1, -1)}
        </sup>,
      );
    }
    lastIndex = match.index + full.length;
    match = pattern.exec(text);
  }
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }
  return nodes;
}

/** Markdown mínimo y seguro (sin HTML crudo): párrafos, listas, negritas, enlaces y citas. */
export function renderMarkdown(text: string): ReactNode {
  const blocks: ReactNode[] = [];
  let items: string[] = [];
  let key = 0;

  const flushList = () => {
    if (items.length === 0) {
      return;
    }
    const listKey = `ul-${key}`;
    key += 1;
    blocks.push(
      <ul key={listKey} className="list-disc space-y-1 pl-5">
        {items.map((item, index) => (
          <li key={`${listKey}-${index}`}>{renderInline(item, `${listKey}-${index}`)}</li>
        ))}
      </ul>,
    );
    items = [];
  };

  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line.startsWith('- ')) {
      items.push(line.slice(2));
      continue;
    }
    flushList();
    if (line !== '') {
      const paragraphKey = `p-${key}`;
      key += 1;
      blocks.push(<p key={paragraphKey}>{renderInline(line, paragraphKey)}</p>);
    }
  }
  flushList();

  return <>{blocks}</>;
}
