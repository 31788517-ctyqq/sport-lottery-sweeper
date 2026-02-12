// Simple test runner for debugging
const { spawn } = require('child_process');
const path = require('path');

console.log('=== Starting Debug Test ===');
console.log('Current directory:', process.cwd());

// Change to frontend directory
process.chdir(path.join(__dirname, 'frontend'));
console.log('Changed to:', process.cwd());

// Run vitest with simple configuration
const vitest = spawn('npx', ['vitest', 'run', 'tests/unit/views/admin/BeidanFilterPanel.unit.spec.js', '--reporter=verbose'], {
  stdio: 'inherit',
  shell: true
});

vitest.on('close', (code) => {
  console.log(`\n=== Test process exited with code ${code} ===`);
});

vitest.on('error', (err) => {
  console.error('Failed to start test process:', err);
});