import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { residences } from './residences';

test('every residence variant uses an existing brochure floor plan', () => {
  for (const residence of residences) {
    for (const variant of residence.variants) {
      assert.ok(variant.floorPlan.startsWith('/ona-assets/floorplans/brochure-'));
      const path = fileURLToPath(new URL(`../../public${variant.floorPlan}`, import.meta.url));
      assert.ok(existsSync(path), `${variant.id}: missing ${variant.floorPlan}`);
    }
  }
  assert.equal(new Set(residences.map(residence => residence.variants[0].floorPlan)).size, 4);
});
