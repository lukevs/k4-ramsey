import fs from 'node:fs';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const read = p => JSON.parse(fs.readFileSync(root + p, 'utf8'));
const rows = read('data/published_cayley_768.json').red_rows;
const fibers = read('reports/pilot-algebraic-lift-001/quotient.json').fibers;
const B = read('reports/literature-two-parameter-001/graphon-candidate.json').red_probability_numerators;
const R = read('experiments/round4_E11/rule.json').types;
const V = read('experiments/round4_E11/perm.json').vertex_of;
const families = Array.from({ length: 12 }, (_, i) => [Math.floor(i / 2) % 3, i % 2, Math.floor(i / 6)]);
function type(u, v) {
  const da = (u[0] - v[0] + 3) % 3, de = u[1] ^ v[1], ds = u[2] ^ v[2];
  return ds ? (da ? 'Z' : 'P') : da ? (de ? 'Z' : 'X') : de ? 'H' : 'Z';
}
const types = families.map(u => families.map(v => type(u, v)));
function search(a = []) {
  if (a.length === 12) return a;
  const k = a.length;
  for (let c = 0; c < 12; c++) {
    if (!a.includes(c) && a.every((v, j) => R[k][j] === types[c][v])) {
      const result = search([...a, c]);
      if (result) return result;
    }
  }
}
const iso = search();
assert(iso);
const order192 = families.flatMap((_, s) => Array.from({ length: 16 }, (_, x) => V[`${iso.indexOf(s)},${x}`]));
assert.equal(new Set(order192).size, 192);
const order = order192.flatMap(i => fibers[i]);
assert.equal(new Set(order).size, 768);
const expected = (t, z) => {
  const c = [0, 1, 2, 4, 8, 15].includes(z);
  return t === 'Z' ? (c ? 0 : 65536) : t === 'X' ? (c ? 65536 : 0) : t === 'P' ? (c ? 51064 : 0) : z === 0 ? 35015 : c ? 65536 : 0;
};
let promoted = 0;
for (let i = 0; i < 192; i++) for (let j = 0; j < 192; j++) {
  const e = expected(types[i >> 4][j >> 4], (i % 16) ^ (j % 16));
  assert.equal(B[order192[i]][order192[j]], e);
  const count = fibers[order192[i]].reduce((s, u) => s + fibers[order192[j]].reduce((t, v) => t + Number(rows[u][v]), 0), 0);
  if (i >> 4 === j >> 4) assert.equal(count, e === 65536 ? 16 : 0);
  if (i < j && e === 51064 && count === 16) promoted++;
  assert([0, 8, 12, 16].includes(count));
}
assert.equal(promoted, 96);
const packed = Buffer.alloc(768 * 768 / 8);
for (let i = 0; i < 768; i++) for (let j = 0; j < 768; j++) {
  assert.equal(rows[order[i]][order[j]], rows[order[j]][order[i]]);
  if (rows[order[i]][order[j]] === '1') packed[(i * 768 + j) >> 3] |= 1 << (j % 8);
}
const data = JSON.stringify({ families, types, order, bits: packed.toString('base64') });
const template = fs.readFileSync(root + 'research/clebsch-explorer.template.html', 'utf8');
assert(template.includes('/* CONSTRUCTION_DATA */ null'));
fs.writeFileSync(root + 'research/clebsch-explorer.html', template.replace('/* CONSTRUCTION_DATA */ null', data));
console.log('Built standalone explorer. Verified all 36,864 B192 entries, 768-vertex symmetry, twelve internal blow-ups, and 96 promoted pairs.');
