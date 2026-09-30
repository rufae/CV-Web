import { renderToStaticMarkup } from 'react-dom/server';

import App from './app/App';

/** Entrada de prerender: genera el HTML inicial de la home para SEO. */
export function render(): string {
  return renderToStaticMarkup(<App />);
}
