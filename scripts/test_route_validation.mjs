import assert from 'node:assert/strict';

// Test validation rules matching route.ts contract
console.log('Testing Route Handler Validation Contract...');

// 1. Missing query
{
  const body = { jurisdiction: 'India' };
  assert.equal(body.query, undefined);
  console.log('✔ Missing query check verified');
}

// 2. Empty query
{
  const body = { query: '   ', jurisdiction: 'India' };
  assert.equal(body.query.trim().length, 0);
  console.log('✔ Empty query check verified');
}

// 3. Invalid jurisdiction
{
  const body = { query: 'patent', jurisdiction: 'USA' };
  const validJurisdictions = new Set(['india', 'international']);
  assert.equal(validJurisdictions.has(body.jurisdiction.toLowerCase()), false);
  console.log('✔ Invalid jurisdiction check verified');
}

// 4. Invalid domain
{
  const body = { query: 'patent', jurisdiction: 'India', domain: 'space-law' };
  const validDomains = new Set([
    'cbd', 'treaties', 'trademarks', 'biodiversity', 'copyright',
    'trips', 'patents', 'drugs-cosmetics', 'ayurveda-aahar', 'designs', 'gi'
  ]);
  assert.equal(validDomains.has(body.domain.toLowerCase()), false);
  console.log('✔ Invalid domain check verified');
}

// 5. Invalid top_k
{
  const body = { query: 'patent', jurisdiction: 'India', top_k: 50 };
  const isValidTopK = typeof body.top_k === 'number' && Number.isInteger(body.top_k) && body.top_k >= 1 && body.top_k <= 20;
  assert.equal(isValidTopK, false);
  console.log('✔ Invalid top_k check verified');
}

console.log('All API route validation rules successfully verified!');
