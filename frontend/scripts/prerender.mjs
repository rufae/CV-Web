import { readFile, writeFile } from 'node:fs/promises';

const template = await readFile('dist/index.html', 'utf8');
const { render } = await import('../dist-ssr/prerender.js');

const html = render();
const marker = '<div id="root"></div>';
if (!template.includes(marker)) {
  throw new Error('No se encontró el contenedor #root en dist/index.html');
}

await writeFile('dist/index.html', template.replace(marker, `<div id="root">${html}</div>`));
console.log('Prerender completado: HTML inicial con contenido');
