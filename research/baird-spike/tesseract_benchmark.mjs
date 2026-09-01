import { createWorker } from 'tesseract.js';
import { readdir, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import os from 'node:os';

const root = path.dirname(fileURLToPath(import.meta.url));
const sheets = path.join(root, 'sheets');
const files = (await readdir(sheets)).filter((name) => name.endsWith('.jpg')).sort();
const started = performance.now();
const worker = await createWorker('eng', 1, { logger: () => {} });
const initMs = performance.now() - started;
const runs = [];
for (const name of files) {
  for (let iteration = 1; iteration <= 3; iteration++) {
    const before = performance.now();
    const result = await worker.recognize(path.join(sheets, name));
    const elapsed = performance.now() - before;
    const row = {
      case_id: path.basename(name, '.jpg'),
      iteration,
      recognition_ms: Math.round(elapsed * 100) / 100,
      confidence: result.data.confidence,
      text: result.data.text.replace(/\s+/g, ' ').trim()
    };
    runs.push(row);
    console.log(row.case_id, iteration, row.recognition_ms, row.confidence);
  }
}
await worker.terminate();
const values = runs.map((row) => row.recognition_ms).sort((a, b) => a - b);
const percentile = (q) => values[Math.max(0, Math.ceil(values.length * q) - 1)];
const report = {
  tesseract_js: '6.0.1',
  node: process.version,
  platform: `${os.platform()} ${os.arch()}`,
  init_ms: Math.round(initMs * 100) / 100,
  run_count: runs.length,
  p50_ms: percentile(0.5),
  p95_ms: percentile(0.95),
  max_ms: Math.max(...values),
  runs
};
await writeFile(path.join(root, 'results', 'tesseract-timings.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ ...report, runs: undefined }, null, 2));
