import assert from 'node:assert/strict';
import { test } from 'node:test';
import { errorMessage, getErrorMessage } from './errors';

test('preserves application errors and reads FastAPI diagnostics', () => {
  assert.equal(errorMessage({ error: { message: 'Invalid credentials' } }, 401), 'Invalid credentials');
  assert.equal(errorMessage({ detail: 'Database connection unavailable' }, 503), 'Database connection unavailable');
  assert.equal(errorMessage({ message: 'Unavailable' }, 503), 'Unavailable');
  assert.equal(errorMessage({ detail: { errors: ['First', 'Second'] } }, 503), 'First; Second');
  assert.equal(errorMessage({ detail: [{ msg: 'Required field' }] }, 422), 'Required field');
});

test('malformed and non-JSON errors use a readable fallback', async () => {
  for (const body of [null, [], { detail: {} }, { error: { message: {} } }, { detail: { errors: [null, {}] } }]) {
    assert.equal(errorMessage(body, 500), 'Request failed with status 500.');
  }
  assert.equal(await getErrorMessage(new Response('<html>Error</html>', { status: 502 })), 'Request failed with status 502.');
});
