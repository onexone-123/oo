const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const dir = fs.existsSync(path.join(__dirname, 'dist/index.html')) ? path.join(__dirname, 'dist') : __dirname;
const model = require(path.join(dir, 'model.js'));
let branches = 0;
for (const color of ['blue', 'white', 'black']) for (const route of ['walk', 'bookshop']) for (const rain of ['continue', 'shelter']) for (const memory of ['sound', 'light']) {
  const r = model.recap({ color, route, rain, memory });
  assert.equal(r.color, model.colors[color].label);
  assert.equal(r.place, rain === 'shelter' ? '屋檐下看雨' : route === 'bookshop' ? '去了街角书店' : '沿着街道慢慢走');
  assert.equal(r.detail, memory === 'sound' ? '雨落下来的声音' : '雨后街角的光');
  branches++;
}
assert.throws(() => model.recap(model.initialState()));
const test = model.rateDifference(200, 36, 200, 44);
assert.equal(test.a, .18); assert.equal(test.b, .22);
assert.ok(Math.abs(test.delta - .04) < 1e-12);
assert.ok(test.containsZero && test.low < 0 && test.high > 0);
assert.ok(model.rateDifference(200, 201, 200, 44).error);
assert.ok(model.rateDifference(0, 0, 1, 1).error);
assert.ok(model.rateDifference(NaN, 0, 200, 2).error);
assert.ok(model.rateDifference(2.5, 1, 2, 1).error);
for (const counts of [[1, 0, 1, 0], [1, 1, 1, 1], [1, 0, 1, 1], [1000, 0, 1000, 1000]]) {
  const r = model.rateDifference(...counts);
  assert.ok(Number.isFinite(r.low) && Number.isFinite(r.high));
  assert.ok(r.low >= -1 && r.high <= 1 && r.low <= r.delta && r.high >= r.delta);
}
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
assert.equal(ids.length, new Set(ids).size, 'Duplicate HTML id');
for (const match of html.matchAll(/href="#([^"]+)"/g)) assert.ok(ids.includes(match[1]), `Broken anchor ${match[1]}`);
const offline = fs.readFileSync(path.join(dir, 'offline.html'), 'utf8');
assert.ok(!/<script[^>]+src=|<link[^>]+rel="stylesheet"/.test(offline));
assert.ok(offline.includes('function rateDifference') && offline.includes('DOMContentLoaded'));
console.log(`Verified ${branches} complete story branches, metric validation and interval edges, anchors and offline packaging.`);
