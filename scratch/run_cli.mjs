import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);
const baseDir = process.cwd();

// Load .env.local
const envLocalPath = path.join(baseDir, '.env.local');
const env = { ...process.env, PYTHONIOENCODING: 'utf-8' };
if (fs.existsSync(envLocalPath)) {
  const content = fs.readFileSync(envLocalPath, 'utf-8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
      const [k, v] = trimmed.split('=');
      env[k.trim()] = v.trim();
    }
  }
}

const payload = {
  productName: 'Ashwagandha Wellness Tablet',
  category: 'Ayurveda-Aahar',
  form: 'Tablet',
  description: 'Standardized herbal tablet formulation intended for general wellness, using traditional processing methods.',
  ingredients: [
    { name: 'Ashwagandha (Withania somnifera)', quantity: '500', unit: 'mg' },
    { name: 'Pippali (Piper longum)', quantity: '50', unit: 'mg' },
    { name: 'Black Pepper', quantity: '25', unit: 'mg' }
  ],
  jurisdiction: 'India'
};

env.PRODUCT_PAYLOAD = JSON.stringify(payload);

const pythonPath = path.join(baseDir, '.venv', 'Scripts', 'python.exe');
const scriptPath = path.join(baseDir, 'scripts', 'product_analysis_api.py');

console.log('=== RUNNING CLI BRIDGE PRODUCT ANALYSIS VERIFICATION ===');
const t0 = Date.now();

try {
  const { stdout, stderr } = await execFileAsync(pythonPath, [scriptPath, '--analysis-id', 'test-cli-run-1'], {
    cwd: baseDir,
    env,
    maxBuffer: 10 * 1024 * 1024,
    shell: true,
  });

  const t1 = Date.now();
  console.log(`Total Pipeline Execution Time: ${t1 - t0} ms (${((t1 - t0) / 1000).toFixed(2)} seconds)`);

  if (stderr) {
    console.log('STDERR:', stderr.substring(0, 300));
  }

  const result = JSON.parse(stdout);
  console.log('\n=== RESULT METRICS ===');
  console.log('Analysis ID:', result.analysis_id);
  console.log('Abstained:', result.abstained);
  console.log('Evidence Strength:', result.evidence_strength);
  console.log('Requires Human Review:', result.requires_human_review);
  console.log('Citations Count:', result.citations ? result.citations.length : 0);
  console.log('Citations:', result.citations);

  console.log('\n=== COMPLIANCE CHECKLIST (' + (result.compliance_checklist ? result.compliance_checklist.length : 0) + ' items) ===');
  console.log(JSON.stringify(result.compliance_checklist, null, 2));

  console.log('\n=== GROUNDED SUMMARY (First 250 chars) ===');
  console.log(String(result.grounded_summary || '').substring(0, 250) + '...');
} catch (err) {
  console.error('CLI Execution Error:', err);
}
