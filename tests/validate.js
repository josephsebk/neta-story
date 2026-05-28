#!/usr/bin/env node
/* ==========================================================================
 * Static structural test suite for the neta-story site.
 * Run:  node tests/validate.js
 *
 * It checks, without a browser:
 *   1. data.js / app.js parse cleanly and NETA_DATA loads
 *   2. Every getElementById / querySelector("#id") in app.js has a
 *      matching element in index.html
 *   3. Every local asset referenced in index.html exists on disk
 *   4. Expected NETA_DATA arrays exist and have the right shape
 *   5. Coin clamp() sizes keep gold/silver growth ratios sane
 * ======================================================================== */

const fs   = require("fs");
const path = require("path");
const vm   = require("vm");

const ROOT = path.resolve(__dirname, "..");
const read = f => fs.readFileSync(path.join(ROOT, f), "utf8");

let pass = 0, fail = 0;
const ok   = m => { pass++; console.log("  ✓ " + m); };
const bad  = m => { fail++; console.log("  ✗ " + m); };
function section(t) { console.log("\n" + t); }

// ---------------------------------------------------------------------------
// 1. Parse data.js in a sandbox and expose NETA_DATA
// ---------------------------------------------------------------------------
section("1. Script parsing");
const sandbox = { window: {}, console };
let data = null;
try {
  vm.runInNewContext(read("data.js"), sandbox);
  data = sandbox.window.NETA_DATA;
  data ? ok("data.js parses and defines window.NETA_DATA")
       : bad("data.js parsed but NETA_DATA is undefined");
} catch (e) { bad("data.js threw: " + e.message); }

// app.js: syntax-check by compiling (don't execute — it needs the DOM)
try {
  new vm.Script(read("app.js"), { filename: "app.js" });
  ok("app.js compiles (no syntax errors)");
} catch (e) { bad("app.js syntax error: " + e.message); }

const html = read("index.html");

// ---------------------------------------------------------------------------
// 2. DOM IDs referenced from app.js must exist in index.html
// ---------------------------------------------------------------------------
section("2. DOM id wiring (app.js → index.html)");
const appjs = read("app.js");
const idRefs = new Set();
for (const m of appjs.matchAll(/getElementById\(\s*["'`]([^"'`]+)["'`]\s*\)/g)) idRefs.add(m[1]);
for (const m of appjs.matchAll(/querySelector\(\s*["'`]#([A-Za-z0-9_-]+)["'`]\s*\)/g)) idRefs.add(m[1]);

const htmlIds = new Set([...html.matchAll(/\sid=["']([^"']+)["']/g)].map(m => m[1]));
if (idRefs.size === 0) bad("no element ids referenced from app.js (unexpected)");
for (const id of [...idRefs].sort()) {
  htmlIds.has(id) ? ok(`#${id} present`) : bad(`#${id} referenced in app.js but MISSING from index.html`);
}

// ---------------------------------------------------------------------------
// 3. Local assets referenced in index.html must exist
// ---------------------------------------------------------------------------
section("3. Local asset references");
const assetRefs = new Set();
for (const m of html.matchAll(/(?:src|href)=["']([^"']+)["']/g)) {
  const u = m[1];
  // Skip external (http/https), protocol-relative (//cdn...), anchors, data URIs
  if (u.startsWith("http") || u.startsWith("//") || u.startsWith("#") || u.startsWith("data:")) continue;
  assetRefs.add(u);
}
for (const rel of [...assetRefs].sort()) {
  fs.existsSync(path.join(ROOT, rel)) ? ok(`${rel} exists`)
                                      : bad(`${rel} referenced but NOT found on disk`);
}

// ---------------------------------------------------------------------------
// 4. NETA_DATA shape
// ---------------------------------------------------------------------------
section("4. Data integrity");
if (data) {
  const expectArr = (key, min) => {
    const v = data[key];
    Array.isArray(v) && v.length >= min
      ? ok(`${key}: ${v.length} rows`)
      : bad(`${key}: expected array ≥ ${min}, got ${v && v.length}`);
  };
  expectArr("indices", 4);
  expectArr("preferredStocks", 10);
  expectArr("preferredStocksByAum", 10);
  expectArr("preferredFunds", 10);
  expectArr("preferredFundsByAum", 10);
  expectArr("superPickers", 5);
  expectArr("partyPerformance", 5);
  expectArr("globalAssets", 3);
  expectArr("topGoldHolders", 5);
  expectArr("topSilverHolders", 5);

  // leaderboards
  const lb = data.leaderboards || {};
  ["bestReturn", "worstReturn"].forEach(k =>
    Array.isArray(lb[k]) && lb[k].length >= 5 ? ok(`leaderboards.${k}: ${lb[k].length}`)
                                              : bad(`leaderboards.${k} missing/short`));

  // every preferred row needs the fields the renderer reads
  const checkRows = (key, fields) => (data[key] || []).forEach((r, i) => {
    const miss = fields.filter(f => r[f] === undefined);
    if (miss.length) bad(`${key}[${i}] missing: ${miss.join(", ")}`);
  });
  checkRows("preferredStocks",      ["ticker", "name", "domain", "holders", "aumCr", "returnPct"]);
  checkRows("preferredStocksByAum", ["ticker", "name", "domain", "holders", "aumCr", "returnPct"]);
  checkRows("preferredFunds",       ["name", "house", "domain", "holders", "aumCr", "returnPct"]);
  checkRows("preferredFundsByAum",  ["name", "house", "domain", "holders", "aumCr", "returnPct"]);
  ok("preferred* rows carry all renderer fields");
} else {
  bad("skipping data checks — NETA_DATA not loaded");
}

// ---------------------------------------------------------------------------
// 5. Logo manifest domains all have a local file
// ---------------------------------------------------------------------------
section("5. Logo manifest ↔ files");
const manMatch = appjs.match(/LOGO_MANIFEST\s*=\s*\{([\s\S]*?)\};/);
if (manMatch) {
  const pairs = [...manMatch[1].matchAll(/"([^"]+)":\s*"([^"]+)"/g)];
  pairs.length ? null : bad("LOGO_MANIFEST parsed but empty");
  for (const [, domain, file] of pairs) {
    fs.existsSync(path.join(ROOT, file)) ? ok(`${domain} → ${file}`)
                                         : bad(`${domain} → ${file} MISSING`);
  }
} else bad("LOGO_MANIFEST not found in app.js");

// ---------------------------------------------------------------------------
// 6. Coin clamp() growth ratios
// ---------------------------------------------------------------------------
section("6. Coin sizing sanity");
const coinClamps = [...html.matchAll(/--coin-size:\s*clamp\((\d+)px,\s*([\d.]+)vw,\s*(\d+)px\)/g)]
  .map(m => ({ min: +m[1], vw: +m[2], max: +m[3] }));
if (coinClamps.length === 4) {
  ok(`found 4 coin clamps`);
  // mobile floor should be modest (< 160px) so coins don't dominate phones
  coinClamps.forEach((c, i) => {
    c.min <= 160 ? ok(`coin[${i}] mobile floor ${c.min}px is reasonable`)
                 : bad(`coin[${i}] mobile floor ${c.min}px too large for phones`);
  });
  // gold ratio (big/small) and silver ratio at the max breakpoint
  const goldRatio   = coinClamps[1].max / coinClamps[0].max;
  const silverRatio = coinClamps[3].max / coinClamps[2].max;
  Math.abs(goldRatio   - 2.19) < 0.4 ? ok(`gold growth ratio ~${goldRatio.toFixed(2)}x`)   : bad(`gold ratio off: ${goldRatio.toFixed(2)}`);
  Math.abs(silverRatio - 3.06) < 0.5 ? ok(`silver growth ratio ~${silverRatio.toFixed(2)}x`) : bad(`silver ratio off: ${silverRatio.toFixed(2)}`);
} else {
  bad(`expected 4 coin clamps, found ${coinClamps.length}`);
}

// ---------------------------------------------------------------------------
console.log(`\n${"=".repeat(48)}`);
console.log(`  ${pass} passed, ${fail} failed`);
console.log("=".repeat(48));
process.exit(fail ? 1 : 0);
