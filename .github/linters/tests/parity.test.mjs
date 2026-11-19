// Optional migration oracle. Supply an independently installed, reviewed
// markdownlint-cli 0.49.1 baseline with the original lockfile in the sandbox.
// It is deliberately NOT a production dependency of the new adapter.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import { markdownFiles } from "../markdown-files.mjs";

const baseline = process.env.MARKDOWNLINT_BASELINE_CLI;
const wrapper = fileURLToPath(new URL("../run-markdownlint.mjs", import.meta.url));
const rule = fileURLToPath(new URL("./fixtures/selection-rule.cjs", import.meta.url));
const ignores = ["node_modules", ".github/linters/node_modules", "CHANGELOG.md", "MIGRATION.md"];
const oldArgs = ["--dot", "**/*.md", ...ignores.flatMap((name) => ["-i", name])];

function invoke(script, args, cwd, env = process.env) {
  const result = spawnSync(process.execPath, [script, ...args], { cwd, env, encoding: "utf8", timeout: 60000 });
  assert.ifError(result.error);
  assert.equal(result.signal, null);
  return result;
}

function selection(root, log) {
  const result = invoke(baseline, [...oldArgs, "--rules", rule, "--enable", "TESTSELECT", "--"], root,
    { ...process.env, MARKDOWN_SELECTION_LOG: log });
  assert.ok([0, 1].includes(result.status), result.stderr);
  const selected = fs.readFileSync(log, "utf8").trim().split("\n").map(JSON.parse).sort();
  assert.deepEqual(markdownFiles(root), selected);
  assert.equal(invoke(wrapper, ["--count-only"], root).stdout, `${selected.length}\n`);
}

test("complete baseline selection and diagnostics on the real repository", { skip: !baseline }, (t) => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "markdown-parity-"));
  t.after(() => fs.rmSync(temp, { recursive: true, force: true }));
  const root = fileURLToPath(new URL("../../..", import.meta.url));
  selection(root, path.join(temp, "selection.jsonl"));
  const old = invoke(baseline, oldArgs, root);
  const current = invoke(wrapper, [], root);
  assert.equal(current.status, old.status);
  assert.equal(current.stderr, old.stderr);
  assert.equal(current.stdout, old.stdout);
});

test("synthetic baseline selection, diagnostics and one-pass fix bytes", { skip: !baseline }, (t) => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "markdown-parity-"));
  t.after(() => fs.rmSync(temp, { recursive: true, force: true }));
  const oldRoot = path.join(temp, "old");
  const newRoot = path.join(temp, "new");
  const contents = {
    ".markdownlint.yaml": "default: false\nMD001: true\nMD009: true\nMD012: true\nMD018: true\nMD047: true\nMD013:\n  line_length: 20\n  severity: warning\n",
    ".markdownlintignore": "ignored.md\n*.skip.md\n!keep.skip.md\n",
    "a.md": "# A\n\n### Skipped level\n\n#Missing\n\ntext   ",
    "bom.md": "\uFEFFtext", "crlf.md": "# H\r\n\r\ntext   \r\n",
    "eof.md": "text\n\n\n", "warning.md": "a very long line exceeding twenty columns\n",
    ".hidden/space é.md": "text", ".agents/skills/a.md": "clean\n",
    "upper.MD": "text", "CHANGELOG.md": "excluded",
    "MIGRATION.md": "excluded", "templates/yes.md": "text",
    "node_modules/no.md": "excluded", ".github/linters/node_modules/no.md": "excluded",
    "deep/fixtures/yes.md": "text", "fixtures/yes.md": "text",
    "deep/node_modules/yes.md": "text", "deep/CHANGELOG.md": "text",
    "deep/MIGRATION.md": "text", "deleteme/yes.md": "text",
    "ignored.md": "excluded", "other.skip.md": "excluded", "keep.skip.md": "text",
  };
  for (const root of [oldRoot, newRoot]) {
    for (const [name, text] of Object.entries(contents)) {
      fs.mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
      fs.writeFileSync(path.join(root, name), text);
    }
    fs.symlinkSync(".agents/skills", path.join(root, "skills"), "dir");
    fs.symlinkSync("a.md", path.join(root, "alias.md"), "file");
  }
  selection(newRoot, path.join(temp, "selection.jsonl"));
  for (const fix of [false, true]) {
    const old = invoke(baseline, [...oldArgs, ...(fix ? ["--fix"] : [])], oldRoot);
    const current = invoke(wrapper, fix ? ["--fix"] : [], newRoot);
    assert.equal(current.status, old.status);
    assert.equal(current.stderr, old.stderr);
    assert.equal(current.stdout, old.stdout);
    for (const name of Object.keys(contents)) {
      assert.deepEqual(fs.readFileSync(path.join(newRoot, name)), fs.readFileSync(path.join(oldRoot, name)), name);
    }
  }
});
