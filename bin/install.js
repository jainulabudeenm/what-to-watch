#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILLS = ['what-to-watch', 'watch-log'];
const SCRIPTS = ['import-history.py', 'pull-must.py'];
const PKG = path.join(__dirname, '..');

const args = process.argv.slice(2);
const isProject = args.includes('--project') || args.includes('-p');

console.log(`\nwhat-to-watch installer\n`);

// Claude Code reads ~/.agents/skills/, Claude.ai reads ~/.claude/skills/.
// Install to both so it works wherever you are.
const base = isProject ? process.cwd() : os.homedir();
const targets = [
  path.join(base, '.agents', 'skills'),
  path.join(base, '.claude', 'skills'),
];

let anySuccess = false;

for (const name of SKILLS) {
  const src = path.join(PKG, 'skills', `${name}.skill`);
  if (!fs.existsSync(src)) {
    console.error(`Skill file ${name}.skill not found in package. Try reinstalling.`);
    process.exit(1);
  }
  for (const targetDir of targets) {
    const targetFile = path.join(targetDir, `${name}.skill`);
    try {
      fs.mkdirSync(targetDir, { recursive: true });
      fs.copyFileSync(src, targetFile);
      console.log(`installed: ${targetFile}`);
      anySuccess = true;
    } catch (err) {
      console.warn(`could not install to ${targetDir}: ${err.message}`);
    }
  }
}

if (!anySuccess) {
  console.error('Installation failed. Check folder permissions.');
  process.exit(1);
}

// The importers have to land somewhere the skill can find them by a fixed path,
// because an npx install has no repo checkout to point at.
const dataDir = path.join(os.homedir(), '.claude', 'what-to-watch');
try {
  fs.mkdirSync(dataDir, { recursive: true });
  for (const s of SCRIPTS) {
    fs.copyFileSync(path.join(PKG, 'scripts', s), path.join(dataDir, s));
  }
  console.log(`installed: ${path.join(dataDir, '{' + SCRIPTS.join(',') + '}')}`);
} catch (err) {
  console.warn(`could not install the importers: ${err.message}`);
  console.warn(`Grab them from https://github.com/jainulabudeenm/what-to-watch/tree/main/scripts`);
}

if (isProject) {
  console.log(`\nTip: commit .agents/skills/ and .claude/skills/ to share with your team.`);
}

console.log(`\nHow to use:`);
console.log(`   Ask "what should I watch tonight" and answer the few questions it asks back`);
console.log(`   First run walks you through importing your history and building a taste profile`);
console.log(`   Say "log my watches" to capture what you thought of something`);

console.log(`\nImporting a history you already have:`);
console.log(`   MUST         python3 ~/.claude/what-to-watch/pull-must.py <username>`);
console.log(`   Letterboxd   export your data, then point the importer at the csv files`);
console.log(`   Trakt        any export tool that gives you the api shaped json`);
console.log(`   then         python3 ~/.claude/what-to-watch/import-history.py <files>`);

console.log(`\nAlso installable as a Claude Code plugin, which adds the`);
console.log(`/what-to-watch-init and /watch-log-scan commands:`);
console.log(`  /plugin marketplace add jainulabudeenm/what-to-watch`);
console.log(`  /plugin install what-to-watch`);

console.log(`\nTo update later: npx @jainulabudeenm/what-to-watch@latest\n`);
