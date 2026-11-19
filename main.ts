// news-image-20261119 entrypoint (Node 22, standard library only).
//
// What the grader runs. It writes the entry image to the output directory
// (MAKEFUN_OUTPUT_DIR locally, /output in the grader):
//
//   1. It tries to draw the front page fresh: python3 render.py into a
//      temporary directory, then takes that entry.png.
//   2. If Python or PIL is unavailable (the grader's container is standard
//      library only), it falls back to the committed entry.png beside this
//      file -- which is the same renderer's output, byte for byte, because
//      render.py is deterministic.
//   3. It checks the image against the gate (PNG or JPEG signature, at
//      most 1 MiB) and copies it to <output>/entry.png.
//
// Run locally:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const root = new URL('.', import.meta.url).pathname;
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1048576;

mkdirSync(outDir, { recursive: true });

// --- step 1: a fresh render, when the runtime allows it -------------------
let produced = null;
const staging = mkdtempSync(join(tmpdir(), 'news-image-20261119-'));
try {
  execFileSync('python3', [join(root, 'render.py'), staging],
               { stdio: 'pipe', timeout: 55000 });
  const candidate = join(staging, 'entry.png');
  if (existsSync(candidate)) produced = candidate;
} catch {
  produced = null; // fall through to the committed image
}

// --- step 2: the committed image ------------------------------------------
if (!produced) {
  const committed = join(root, 'entry.png');
  if (existsSync(committed)) produced = committed;
}
if (!produced) {
  console.error('main.ts: no entry image could be produced');
  process.exit(1);
}

// --- step 3: gate check, then copy ----------------------------------------
const bytes = readFileSync(produced);
const isPng = bytes.length > 4 && bytes[0] === 0x89 && bytes[1] === 0x50 &&
              bytes[2] === 0x4e && bytes[3] === 0x47;
const isJpeg = bytes.length > 2 && bytes[0] === 0xff && bytes[1] === 0xd8;
if (!isPng && !isJpeg) {
  console.error('main.ts: produced file is neither PNG nor JPEG');
  process.exit(1);
}
if (bytes.length > MAX_BYTES) {
  console.error(`main.ts: entry image is ${bytes.length} bytes, over 1 MiB`);
  process.exit(1);
}

copyFileSync(produced, join(outDir, 'entry.png'));
rmSync(staging, { recursive: true, force: true });
console.log(`main.ts: wrote ${join(outDir, 'entry.png')} (${bytes.length} bytes)`);

// --- the run dossier -------------------------------------------------------
// A small manifest of what was written. It is built only from the image
// bytes and fixed strings -- no clock, no paths -- so it too is identical
// on every run.
const dossier = {
  competition: 'news-image-20261119',
  date: '2026-11-19',
  day: 'Thursday',
  title: 'The World on One Page — Thursday 19 November 2026',
  entry: {
    file: 'entry.png',
    format: isPng ? 'PNG' : 'JPEG',
    bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'),
  },
};
writeFileSync(join(outDir, 'dossier.json'),
              JSON.stringify(dossier, null, 2) + '\n');
console.log(`main.ts: wrote ${join(outDir, 'dossier.json')}`);
