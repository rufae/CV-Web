import { readdir, readFile, writeFile } from 'node:fs/promises';

const reportsDir = new URL('../../eval/reports/', import.meta.url);
const target = new URL('../public/eval-latest.json', import.meta.url);

try {
  const files = (await readdir(reportsDir)).filter((file) => file.endsWith('.json')).sort();
  if (files.length === 0) {
    console.log('Sin informes de evaluación todavía');
  } else {
    const latest = files.at(-1);
    const data = await readFile(new URL(latest, reportsDir), 'utf8');
    await writeFile(target, data);
    console.log(`eval-latest.json actualizado desde ${latest}`);
  }
} catch (error) {
  console.log('No se pudo copiar el informe de evaluación:', String(error));
}
