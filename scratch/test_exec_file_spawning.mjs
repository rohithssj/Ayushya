import { execFile } from 'child_process';
import path from 'path';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);
const baseDir = process.cwd();
const pythonPath = path.join(baseDir, '.venv', 'Scripts', 'python.exe');
const quotedPythonPath = `"${pythonPath}"`;

async function testSpawn(cmd, useShell) {
  try {
    const { stdout } = await execFileAsync(cmd, ['--version'], { cwd: baseDir, shell: useShell });
    console.log(`[cmd=${cmd}, shell=${useShell}] SUCCESS:`, stdout.trim());
    return true;
  } catch (err) {
    console.error(`[cmd=${cmd}, shell=${useShell}] FAILED:`, err.message);
    return false;
  }
}

async function run() {
  await testSpawn(pythonPath, false);
  await testSpawn(pythonPath, true);
  await testSpawn(quotedPythonPath, true);
  await testSpawn('python', false);
  await testSpawn('python', true);
}

run();
