#!/usr/bin/env node
// Shared glob/ignore list for markdownlint, used by both CI and the
// pre-commit hook so the two cannot diverge (same requirement the old
// .markdownlint-cli2.yaml's globs: key enforced, now expressed here instead
// since markdownlint-cli takes globs/ignores as CLI args, not config keys).
//
// Usage:
//   node run-markdownlint.mjs [--fix] [--count-only]
//
// --count-only prints the number of files the glob list matches (via the
// same tinyglobby engine markdownlint-cli uses internally) and exits 0,
// without running the linter. Used by CI to assert the glob list didn't
// silently match zero files.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));

const globs = ["**/*.md"];

const ignores = [
  "node_modules",
  ".github/linters/node_modules",
  "CHANGELOG.md",
  "MIGRATION.md",
];

const args = process.argv.slice(2);
const countOnly = args.includes("--count-only");
const passthroughArgs = args.filter((a) => a !== "--count-only");

if (countOnly) {
  const { globSync } = await import(
    join(here, "node_modules", "tinyglobby", "dist", "index.mjs")
  );
  const files = globSync(globs, { ignore: ignores, dot: true });
  console.log(files.length);
  process.exit(0);
}

const ignoreArgs = ignores.flatMap((i) => ["-i", i]);
const result = spawnSync(
  join(here, "node_modules", ".bin", "markdownlint"),
  ["--dot", ...globs, ...ignoreArgs, ...passthroughArgs],
  { stdio: "inherit" }
);
process.exit(result.status ?? 1);
