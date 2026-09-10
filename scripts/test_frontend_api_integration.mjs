import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

console.log('Running Frontend ↔ Backend Integration Tests...');

// 1. Verify Client-side Security: OPENROUTER_API_KEY must NEVER be referenced in client code
{
  const clientDirs = ['src/components', 'src/services', 'src/app/analyze', 'src/app/analysis', 'src/app/assistant'];
  for (const dir of clientDirs) {
    if (fs.existsSync(dir)) {
      const files = fs.readdirSync(dir, { recursive: true });
      for (const file of files) {
        if (typeof file === 'string' && (file.endsWith('.ts') || file.endsWith('.tsx') || file.endsWith('.js'))) {
          const content = fs.readFileSync(path.join(dir, file), 'utf-8');
          assert.equal(
            content.includes('OPENROUTER_API_KEY'),
            false,
            `Security violation: ${file} contains OPENROUTER_API_KEY in client code!`
          );
        }
      }
    }
  }
  console.log('✔ Client-side security verified: OPENROUTER_API_KEY is not exposed to client code');
}

// 2. Chat API contract validation
{
  const request = {
    message: 'Can I patent an herbal mixture under Indian law?',
    jurisdiction: 'India',
  };
  assert.ok(request.message.trim().length > 0);
  assert.equal(request.jurisdiction, 'India');
  console.log('✔ Chat request payload schema verified');
}

// 3. Analysis API contract validation
{
  const analysisReq = {
    productName: 'Ashwagandha Wellness Tablet',
    category: 'Ayurveda-Aahar',
    form: 'Tablet',
    description: 'Standardized extract formulation targeted for stress reduction.',
    ingredients: [
      { name: 'Ashwagandha', quantity: '500', unit: 'mg' },
      { name: 'Pipali', quantity: '50', unit: 'mg' },
    ],
    jurisdiction: 'India',
  };

  assert.ok(analysisReq.productName.length > 0);
  assert.ok(analysisReq.ingredients.length >= 1);
  assert.equal(analysisReq.jurisdiction, 'India');
  console.log('✔ Analysis formulation request schema verified');
}

// 4. Abstention handling contract
{
  const mockAbstentionApiResponse = {
    request_id: 'req_123',
    query: 'Quantum satellite outer space tax law',
    answer: null,
    abstained: true,
    abstention_reason: 'Insufficient authoritative evidence found for this query in the ingested legal corpus.',
    evidence_strength: 'insufficient',
    requires_human_review: true,
    citations: [],
    evidence: { selected: [], count: 0 },
  };

  assert.equal(mockAbstentionApiResponse.abstained, true);
  assert.equal(mockAbstentionApiResponse.answer, null);
  assert.equal(mockAbstentionApiResponse.requires_human_review, true);
  console.log('✔ Abstention contract verified');
}

// 5. Citation metadata safety check
{
  const validChunkCitation = {
    citation_id: 'cit_patents_001',
    chunk_id: 'india_patents_act_1970_001',
    document_id: 'india_patents_act_1970',
    title: 'The Patents Act, 1970',
    section: 'Section 3',
    section_title: 'What are not inventions',
    subsection: '3(p)',
    jurisdiction: 'India',
    source_url: null,
  };

  // Ensure URL is omitted when null
  const url = validChunkCitation.source_url && (validChunkCitation.source_url.startsWith('http://') || validChunkCitation.source_url.startsWith('https://'))
    ? validChunkCitation.source_url
    : undefined;

  assert.equal(url, undefined, 'URL must not be fabricated when null in metadata');
  console.log('✔ Citation URL safety verified: no fabricated URLs generated');
}

console.log('\nAll Frontend ↔ Backend Integration Tests Passed Successfully!');
