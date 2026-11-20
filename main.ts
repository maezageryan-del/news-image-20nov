// main.ts — news-image-20261120 entry runner.
//
// Reads the pre-rendered front page (entry.png, sitting next to this file)
// and copies it byte-for-byte to $MAKEFUN_OUTPUT_DIR/entry.png, creating the
// output directory first and verifying the written file matches the source
// byte count. Node 22 standard library only; erasable TypeScript.

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");

if (!existsSync(source)) {
  throw new Error(
    `entry.png is missing next to main.ts (looked in ${here}). ` +
      "Run render.py first to produce the front page image."
  );
}

// Guard against copying a truncated or non-PNG file: entry.png must start
// with the PNG signature (89 50 4E 47 0D 0A 1A 0A).
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const head = readFileSync(source).subarray(0, 8);
if (!head.equals(PNG_SIGNATURE)) {
  throw new Error(
    `entry.png in ${here} is not a valid PNG file (bad signature). ` +
      "Re-run render.py to regenerate it."
  );
}

const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
mkdirSync(outDir, { recursive: true });

const target = join(outDir, "entry.png");
copyFileSync(source, target);

const sourceBytes = statSync(source).size;
const writtenBytes = statSync(target).size;
if (writtenBytes !== sourceBytes) {
  throw new Error(
    `entry.png copy mismatch: wrote ${writtenBytes} bytes, expected ${sourceBytes}.`
  );
}

console.log(`entry.png (${sourceBytes} bytes) written to ${target}`);
