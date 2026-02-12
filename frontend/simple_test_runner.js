// Simple test runner that bypasses vitest watch mode issues
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('=== Simple Test Runner ===');

// Change to frontend directory
process.chdir(path.join(__dirname, 'frontend'));
console.log('Working directory:', process.cwd());

// Test 1: Check if component file exists
const componentPath = './src/views/admin/BeidanFilterPanel.vue';
if (fs.existsSync(componentPath)) {
  console.log('✅ Component file exists:', componentPath);
} else {
  console.log('❌ Component file not found:', componentPath);
}

// Test 2: Check if test file exists
const testPath = './tests/unit/views/admin/BeidanFilterPanel.unit.spec.js';
if (fs.existsSync(testPath)) {
  console.log('✅ Test file exists:', testPath);
} else {
  console.log('❌ Test file not found:', testPath);
}

// Test 3: Try running vitest with different approach
console.log('\n=== Running Tests ===');
try {
  // Use timeout to prevent hanging
  const testCommand = `npx vitest run ${testPath} --reporter=verbose --timeout=10000`;
  console.log('Command:', testCommand);
  
  const output = execSync(testCommand, { 
    encoding: 'utf8',
    stdio: 'pipe',
    timeout: 15000 
  });
  
  console.log('Test output:');
  console.log(output);
  
} catch (error) {
  console.log('Test execution result:');
  console.log('Exit code:', error.status);
  console.log('Stdout:', error.stdout || 'No output');
  console.log('Stderr:', error.stderr || 'No error output');
  
  if (error.signal === 'SIGTERM') {
    console.log('\n⚠️  Tests timed out - vitest may be hanging in watch mode');
  }
}

console.log('\n=== Test Runner Complete ===');