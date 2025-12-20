#!/usr/bin/env node
/**
 * Test Runner for Habit Tracker
 *
 * This script:
 * 1. Starts the dev server
 * 2. Waits for it to be ready
 * 3. Runs Puppeteer tests
 * 4. Reports results
 * 5. Cleans up
 */

const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

// Get the project directory from command line or use current directory
const projectDir = process.argv[2] || process.cwd();

console.log('\n' + '='.repeat(70));
console.log('  HABIT TRACKER TEST RUNNER');
console.log('='.repeat(70));
console.log(`Project directory: ${projectDir}\n`);

// Check if we're in the right directory
const packageJsonPath = path.join(projectDir, 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('❌ Error: package.json not found in', projectDir);
  console.error('Please run from project directory or provide path as argument');
  process.exit(1);
}

// Function to check if port is listening
async function isPortReady(port, timeout = 30000) {
  const net = require('net');
  const startTime = Date.now();

  return new Promise((resolve) => {
    const checkPort = () => {
      const socket = new net.Socket();

      socket.setTimeout(1000);
      socket.on('connect', () => {
        socket.destroy();
        resolve(true);
      });

      socket.on('timeout', () => {
        socket.destroy();
        if (Date.now() - startTime < timeout) {
          setTimeout(checkPort, 500);
        } else {
          resolve(false);
        }
      });

      socket.on('error', () => {
        if (Date.now() - startTime < timeout) {
          setTimeout(checkPort, 500);
        } else {
          resolve(false);
        }
      });

      socket.connect(port, 'localhost');
    };

    checkPort();
  });
}

// Main test function
async function runTests() {
  try {
    console.log('📦 Starting dev server...');

    // Start the dev server
    const devServer = spawn('npm', ['run', 'dev'], {
      cwd: projectDir,
      stdio: 'pipe',
      shell: true
    });

    let serverOutput = '';
    devServer.stdout.on('data', (data) => {
      serverOutput += data.toString();
      if (serverOutput.includes('Local:')) {
        console.log('✅ Dev server started');
      }
    });

    devServer.stderr.on('data', (data) => {
      serverOutput += data.toString();
    });

    // Wait for server to be ready
    console.log('⏳ Waiting for server to be ready...');
    const portReady = await isPortReady(5173, 30000);

    if (!portReady) {
      console.error('❌ Server failed to start on port 5173');
      devServer.kill();
      process.exit(1);
    }

    console.log('✅ Server is ready at http://localhost:5173');

    // Here you would run Puppeteer tests
    console.log('\n📝 Ready to run browser tests');
    console.log('   Use Puppeteer or other browser automation tools');
    console.log('   Server will stay running until you stop it with Ctrl+C\n');

    // Keep the server running
    await new Promise((resolve) => {
      process.on('SIGINT', () => {
        console.log('\n\n🛑 Stopping dev server...');
        devServer.kill();
        resolve();
      });
    });

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Run tests
runTests().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
