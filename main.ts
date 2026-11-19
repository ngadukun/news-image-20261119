// news-image-20261119 entry: "The World in One Day" — Thursday 19 November 2026.
//
// The finished front page lives in this repository as entry.png (drawn at
// build time by render.py; see dossier.json for the day's stories and their
// sources). The grader reads exactly one file, /output/entry.png, and this
// program's job is to put entry.png's bytes there, unchanged. It uses only
// the Node 22 standard library, touches no network, and is deterministic:
// the output is a byte-for-byte copy of entry.png, so two runs agree.
//
// Run locally with MAKEFUN_OUTPUT_DIR standing in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from 'node:crypto';
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
} from 'node:fs';
import { join } from 'node:path';

// The competition gate, checked here so a bad image fails loudly instead of
// being graded invalid: PNG or JPEG by first bytes, at most 1 MiB, and for
// a PNG at most 1024 x 1024 pixels (width and height sit at fixed offsets
// in the IHDR chunk that follows the 8-byte signature).
const MAX_BYTES = 1_048_576;
const MAX_SIDE = 1024;

function checkGate(bytes: Buffer): void {
  if (bytes.length > MAX_BYTES) {
    throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);
  }
  const isPng =
    bytes.length > 24 &&
    bytes.subarray(0, 8).equals(
      Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    );
  const isJpeg = bytes.length > 2 && bytes[0] === 0xff && bytes[1] === 0xd8;
  if (!isPng && !isJpeg) {
    throw new Error('entry.png is neither a PNG nor a JPEG by its first bytes');
  }
  if (isPng) {
    const width = bytes.readUInt32BE(16);
    const height = bytes.readUInt32BE(20);
    if (width > MAX_SIDE || height > MAX_SIDE) {
      throw new Error(`entry.png is ${width}x${height}, over 1024x1024`);
    }
    // Wholeness: a complete PNG ends with the IEND chunk — its length
    // (0), type ("IEND") and CRC are the file's last 12 bytes.
    const iend = Buffer.from([
      0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
    ]);
    if (!bytes.subarray(bytes.length - 12).equals(iend)) {
      throw new Error('entry.png does not end with the IEND chunk');
    }
  }
}

const sourcePath = new URL('./entry.png', import.meta.url);
if (!existsSync(sourcePath)) {
  throw new Error('entry.png is missing beside main.ts; nothing to submit');
}

const source = readFileSync(sourcePath);
checkGate(source);
const sourceHash = createHash('sha256').update(source).digest('hex');

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });

const target = join(outDir, 'entry.png');
copyFileSync(sourcePath, target);

const writtenHash = createHash('sha256')
  .update(readFileSync(target))
  .digest('hex');
if (writtenHash !== sourceHash) {
  throw new Error('written entry.png does not match the source bytes');
}
console.log(
  `wrote ${target} (${statSync(target).size} bytes, sha256 ${writtenHash})`,
);
