#!/usr/bin/env node

/**
 * Test script to verify Fly.io backend connection
 * Tests both health check and authentication
 * Run with: node test-backend-connection.js
 */

// Load .env manually
import { readFileSync } from 'fs';

const envFile = readFileSync('.env', 'utf-8');
const env = {};
envFile.split('\n').forEach(line => {
	const match = line.match(/^([^=]+)=(.*)$/);
	if (match) {
		env[match[1]] = match[2].replace(/^["']|["']$/g, '');
	}
});

const BACKEND_URL = env.MAERCHENWEBER_API_URL;
const API_KEY = env.MAERCHENWEBER_API_KEY;

console.log('🔍 Testing Fly.io Backend Connection\n');
console.log('Configuration:');
console.log(`  Backend URL: ${BACKEND_URL}`);
console.log(`  API Key: ${API_KEY ? `${API_KEY.substring(0, 8)}...` : '(not set)'}`);
console.log('');

async function testHealthCheck() {
	console.log('1️⃣ Testing health check endpoint...');
	try {
		const response = await fetch(`${BACKEND_URL}/health`);
		const data = await response.json();
		console.log(`   ✅ Status: ${response.status}`);
		console.log(`   📊 Response:`, data);
		return response.ok;
	} catch (error) {
		console.log(`   ❌ Failed: ${error.message}`);
		return false;
	}
}

async function testAuthentication() {
	console.log('\n2️⃣ Testing authenticated endpoint...');
	try {
		const response = await fetch(`${BACKEND_URL}/adventure/start`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-API-Key': API_KEY
			},
			body: JSON.stringify({
				user_id: 'test-user-123',
				difficulty: 'easy',
				character_name: 'Max',
				character_description: 'Ein mutiger Junge',
				story_theme: 'fantasy'
			})
		});

		console.log(`   ✅ Status: ${response.status}`);

		if (response.ok) {
			const data = await response.json();
			console.log(`   📊 Response: Session started with ID ${data.session_id}`);
			console.log(`   📖 Story has ${data.total_chapters} chapters`);
			return true;
		} else {
			const error = await response.text();
			console.log(`   ⚠️ Response (${response.status}): ${error.substring(0, 200)}`);
			// 422 with validation means auth worked, just bad data format
			return response.status === 422;
		}
	} catch (error) {
		console.log(`   ❌ Failed: ${error.message}`);
		return false;
	}
}

async function testDocumentation() {
	console.log('\n3️⃣ Testing API documentation...');
	try {
		const response = await fetch(`${BACKEND_URL}/docs`);
		console.log(`   ✅ Status: ${response.status}`);
		console.log(`   📖 Docs available at: ${BACKEND_URL}/docs`);
		return response.ok;
	} catch (error) {
		console.log(`   ❌ Failed: ${error.message}`);
		return false;
	}
}

async function runTests() {
	if (!BACKEND_URL) {
		console.log('❌ MAERCHENWEBER_API_URL not set in .env');
		process.exit(1);
	}

	if (!API_KEY) {
		console.log('⚠️ Warning: MAERCHENWEBER_API_KEY not set in .env');
	}

	const healthOk = await testHealthCheck();
	const authOk = await testAuthentication();
	const docsOk = await testDocumentation();

	console.log('\n📋 Summary:');
	console.log(`  Health Check: ${healthOk ? '✅' : '❌'}`);
	console.log(`  Authentication: ${authOk ? '✅' : '❌'}`);
	console.log(`  Documentation: ${docsOk ? '✅' : '❌'}`);

	if (healthOk && authOk) {
		console.log('\n✅ All tests passed! Your SvelteKit app can connect to Fly.io backend.');
	} else {
		console.log('\n❌ Some tests failed. Check the Fly.io deployment.');
	}
}

runTests();
