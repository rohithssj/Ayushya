import { execFile } from 'child_process';
import path from 'path';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);
const baseDir = process.cwd();
const pythonPath = path.join(baseDir, '.venv', 'Scripts', 'python.exe');
const scriptPath = path.join(baseDir, 'scripts', 'product_analysis_api.py');

const payload = {
  productName: "Ashwagandha Wellness Tablet",
  category: "Ayurveda-Aahar",
  form: "Tablet",
  description: "Standardized extract formulation targeted for stress reduction and immunity enhancement using traditional processing methods.",
  ingredients: [
    { name: "Ashwagandha (Withania somnifera)", quantity: "500", unit: "mg" },
    { name: "Pipali (Piper longum)", quantity: "50", unit: "mg" },
    { name: "Black Pepper", quantity: "25", unit: "mg" }
  ],
  jurisdiction: "India"
};

async function testDirectExec(useShell) {
  console.log(`\nTesting execFileAsync with shell=${useShell}...`);
  const args = [
    scriptPath,
    '--payload', JSON.stringify(payload),
    '--analysis-id', `test-${Date.now()}`
  ];

  try {
    const { stdout } = await execFileAsync(pythonPath, args, {
      cwd: baseDir,
      timeout: 120000,
      maxBuffer: 10 * 1024 * 1024,
      shell: useShell,
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8',
        OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY || '',
        LLM_MODEL: process.env.LLM_MODEL || 'nvidia/nemotron-3-super-120b-a12b',
        LLM_FALLBACK_MODELS: process.env.LLM_FALLBACK_MODELS || '',
        LLM_TIMEOUT_SECONDS: process.env.LLM_TIMEOUT_SECONDS || '15',
      }
    });

    const result = JSON.parse(stdout);
    console.log(`[shell=${useShell}] SUCCESS: evidence_strength=${result.evidence_strength}, citations=${result.citations?.length}`);
    return true;
  } catch (err) {
    console.error(`[shell=${useShell}] FAILED:`, err.message);
    return false;
  }
}

async function run() {
  console.log("=== DIRECT EXECUTION VERIFICATION ===");
  const noShellResult = await testDirectExec(false);
  const shellResult = await testDirectExec(true);
}

run();
