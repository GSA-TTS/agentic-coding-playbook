import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import { applyFixes, getVersion } from "markdownlint";
import { lint } from "markdownlint/sync";
import { markdownFiles } from "../markdown-files.mjs";
import { lintFiles, markdownItFactory } from "../run-markdownlint.mjs";

const wrapper = fileURLToPath(new URL("../run-markdownlint.mjs", import.meta.url));
const repositoryConfig = fs.readFileSync(new URL("../../../.markdownlint.yaml", import.meta.url), "utf8");
const config = "default: false\nMD009: true\nMD010: true\nMD012: true\nMD047: true\n";

function fixture(t, contents = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "markdown-adapter-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  put(root, ".markdownlint.yaml", config);
  for (const [name, text] of Object.entries(contents)) put(root, name, text);
  return root;
}

function put(root, name, text) {
  const target = path.join(root, name);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, text);
}

function run(root, ...args) {
  const result = spawnSync(process.execPath, [wrapper, ...args], {
    cwd: root, encoding: "utf8", timeout: 15000,
  });
  assert.ifError(result.error);
  assert.equal(result.signal, null);
  return result;
}

test("pinned engine and the adapter's markdown-it factory really parse HTML", () => {
  assert.equal(getVersion(), "0.41.1");
  let observed = false;
  const result = lint({
    strings: { sample: "<div>\nraw\n</div>\n" },
    config: { default: false, TESTHTML: true },
    markdownItFactory,
    customRules: [{
      names: ["TESTHTML"], tags: ["test"], description: "HTML parser contract",
      parser: "markdownit",
      function(params) {
        observed = true;
        assert.ok(params.parsers.markdownit.tokens.some((token) => token.type === "html_block"));
      },
    }],
  });
  assert.ok(observed);
  assert.deepEqual(result.sample, []);
});

test("fixed selection includes hidden files, lexical aliases, Unicode, fixtures and templates, and nested root names", (t) => {
  const root = fixture(t, {
    "a.md": "ok\n", ".hidden/é space.md": "ok\n", ".root.md": "ok\n",
    "node_modules/no.md": "bad", ".github/linters/node_modules/no.md": "bad",
    "CHANGELOG.md": "bad", "MIGRATION.md": "bad",
    "fixtures/yes.md": "ok\n", "deep/fixtures/yes.md": "ok\n",
    "templates/yes.md": "ok\n", "deleteme/yes.md": "ok\n",
    "deep/node_modules/yes.md": "ok\n", "deep/MIGRATION.md": "ok\n",
    "deep/CHANGELOG.md": "ok\n", ".agents/skills/one.md": "ok\n",
    "not.markdown": "bad", "not.mdx": "bad",
  });
  fs.symlinkSync(".agents/skills", path.join(root, "skills"), "dir");
  fs.symlinkSync("a.md", path.join(root, "alias.md"), "file");
  const expected = [
    ".agents/skills/one.md", ".hidden/é space.md", ".root.md", "a.md", "alias.md",
    "deep/CHANGELOG.md", "deep/MIGRATION.md", "deep/fixtures/yes.md",
    "deep/node_modules/yes.md", "deleteme/yes.md", "fixtures/yes.md",
    "skills/one.md", "templates/yes.md",
  ].sort();
  assert.deepEqual(markdownFiles(root), expected);
  assert.deepEqual(markdownFiles(root), expected);
  assert.equal(run(root, "--count-only").stdout, `${expected.length}\n`);
  assert.equal(run(root).status, 0);
});

test("extension follows CLI platform policy", (t) => {
  const root = fixture(t, { "upper.MD": "ok\n", "lower.md": "ok\n" });
  assert.deepEqual(markdownFiles(root, "linux"), ["lower.md"]);
  for (const platform of ["darwin", "win32"]) {
    assert.deepEqual(markdownFiles(root, platform), ["lower.md", "upper.MD"]);
  }
});

test("ignore-file patterns use maintained ignore semantics, including negation and case", (t) => {
  const root = fixture(t, {
    "a.md": "ok\n", "space name.md": "bad", "deep/skip.md": "bad",
    "deep/keep.md": "ok\n", "UPPER.md": "bad", "#literal.md": "bad",
    ".markdownlintignore": "# comment\nspace name.md\ndeep/*.md\n!deep/keep.md\nupper.md\n\\#literal.md\n",
  });
  assert.deepEqual(markdownFiles(root), ["a.md", "deep/keep.md"]);
  assert.equal(run(root, "--count-only").stdout, "2\n");
  assert.equal(run(root).status, 0);
});

test("fixed directory exclusion does not turn a symlink alias into a subtree ignore", (t) => {
  const root = fixture(t, { "source/a.md": "ok\n" });
  fs.symlinkSync("source", path.join(root, "node_modules"), "dir");
  assert.deepEqual(markdownFiles(root), ["node_modules/a.md", "source/a.md"]);
});

test("cycles, escaping links and broken links fail explicitly instead of dropping files", (t) => {
  for (const kind of ["cycle", "escape", "broken"]) {
    const root = fixture(t, { "a.md": "ok\n", "sub/b.md": "ok\n" });
    const target = kind === "cycle" ? ".." : kind === "escape" ? os.tmpdir() : "missing";
    fs.symlinkSync(target, path.join(root, "sub/link"), "dir");
    const result = run(root, "--count-only");
    assert.equal(result.status, 4, kind);
    assert.equal(result.stdout, "", kind);
    assert.match(result.stderr, /cycle|escapes repository|ENOENT/, kind);
  }
});

test("zero selected files fails for check, fix and count, including all-ignored input", (t) => {
  for (const contents of [{}, { "a.md": "ok\n", ".markdownlintignore": "*.md\n" }, { "CHANGELOG.md": "ok\n", "MIGRATION.md": "ok\n" }]) {
    const root = fixture(t, contents);
    for (const args of [[], ["--fix"], ["--count-only"]]) {
      const result = run(root, ...args);
      assert.equal(result.status, 4);
      assert.equal(result.stdout, "");
      assert.match(result.stderr, /matched no files/);
    }
  }
});

test("only supported wrapper flags are accepted, without changing files", (t) => {
  const root = fixture(t, { "a.md": "bad" });
  for (const flag of ["--json", "--config", "a.md", "--check", "--", "--fix=true"]) {
    assert.equal(run(root, "--fix", flag).status, 4);
    assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), "bad");
  }
  assert.equal(run(root, "--fix", "--count-only").stdout, "1\n");
  assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), "bad");
});

test("diagnostics preserve error/warning severity, location, detail, context and sorting", (t) => {
  const root = fixture(t, { "z.md": "bad", "a.md": "bad" });
  const expected = ["a.md", "z.md"].map((name) =>
    `${name}:1:3 error MD047/single-trailing-newline Files should end with a single newline character\n`
  ).join("");
  const result = run(root);
  assert.equal(result.status, 1);
  assert.equal(result.stdout, "");
  assert.equal(result.stderr, expected);
  put(root, ".markdownlint.yaml", "default: false\nMD047: warning\n");
  const warning = run(root);
  assert.equal(warning.status, 0);
  assert.equal(warning.stderr, expected.replaceAll(" error ", " warning "));
  put(root, ".markdownlint.yaml", "default: false\nMD013:\n  line_length: 3\nMD001: true\nMD018: true\n");
  put(root, "a.md", "# A\n\n### Heading\n\n#Missing\n");
  const detailed = run(root);
  assert.equal(detailed.status, 1);
  assert.match(detailed.stderr, /MD001\/heading-increment .*\[Expected: h2; Actual: h3\]/);
  assert.match(detailed.stderr, /MD018\/no-missing-space-atx .*\[Context: "#Missing"\]/);
  assert.match(detailed.stderr, /MD013\/line-length .*\[Expected: 3; Actual: 11\]/);
});

test("fix handles missing and extra EOF newlines, CRLF and overlapping fixes", (t) => {
  for (const [input, expected] of [
    ["text", "text\n"], ["text\n\n\n", "text\n"],
    ["# T\r\n\r\ntext   \r\n", "# T\r\n\r\ntext\r\n"],
    ["text   ", "text\n"],
  ]) {
    const root = fixture(t, { "a.md": input });
    assert.equal(run(root).status, 1);
    assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), input);
    const fixed = run(root, "--fix");
    assert.equal(fixed.status, 0, fixed.stderr);
    assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), expected);
    assert.equal(run(root, "--fix").status, 0);
    assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), expected);
  }
});

test("BOM fix output preserves the engine's single-pass behavior", (t) => {
  const input = "\uFEFFtext";
  const root = fixture(t, { "a.md": input });
  const errors = lint({ strings: { sample: input }, config: { default: false, MD047: true } }).sample;
  const expected = applyFixes(input, errors);
  run(root, "--fix");
  assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), expected);
});

test("fix relints and leaves an unfixable violation failing", (t) => {
  const root = fixture(t, { "a.md": "too long" });
  put(root, ".markdownlint.yaml", "default: false\nMD047: true\nMD013:\n  line_length: 3\n");
  const result = run(root, "--fix");
  assert.equal(result.status, 1);
  assert.match(result.stderr, /MD013/);
  assert.doesNotMatch(result.stderr, /MD047/);
  assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), "too long\n");
});

test("repository rule configuration, default frontmatter and inline directives are retained", (t) => {
  const root = fixture(t, {
    "a.md": "---\ntitle: Example\n---\n\n<div>HTML allowed</div>\n\n<!-- markdownlint-disable MD047 -->\ntext",
  });
  put(root, ".markdownlint.yaml", repositoryConfig);
  assert.equal(run(root).status, 0);
  put(root, "a.md", "---\ntitle: Example\n---\n\ntext");
  const result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /^a\.md:5:4 error MD047/m);
});

test("explicit YAML supports extends and rejects malformed, missing and unreadable config", (t) => {
  const root = fixture(t, { "a.md": "text" });
  put(root, "parent.yaml", "default: false\nMD047: true\n");
  put(root, ".markdownlint.yaml", "extends: parent.yaml\n");
  assert.equal(run(root).status, 1);
  put(root, ".markdownlint.yaml", "extends: missing.yaml\n");
  assert.equal(run(root, "--fix").status, 4);
  put(root, ".markdownlint.yaml", "MD047: [\n");
  assert.equal(run(root).status, 4);
  fs.unlinkSync(path.join(root, ".markdownlint.yaml"));
  assert.equal(run(root).status, 4);
  fs.mkdirSync(path.join(root, ".markdownlint.yaml"));
  assert.equal(run(root).status, 4);
  assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), "text");
});

test("required and extended configuration reject non-mappings before fixes", (t) => {
  const root = fixture(t, { "a.md": "text" });
  for (const text of ["null\n", "true\n", "42\n", "scalar\n", "- MD047\n", "[]\n", "\n",
    "2026-11-17\n", "2026-11-17T12:00:00Z\n", "!!binary YWJj\n"]) {
    for (const extended of [false, true]) {
      put(root, ".markdownlint.yaml", extended ? "extends: parent.yaml\n" : text);
      put(root, "parent.yaml", text);
      for (const args of [[], ["--fix"]]) {
        const result = run(root, ...args);
        assert.equal(result.status, 4, `${JSON.stringify({ text, extended, args })}: ${result.stderr}`);
        assert.equal(fs.readFileSync(path.join(root, "a.md"), "utf8"), "text");
      }
    }
  }
  put(root, ".markdownlint.yaml", "{}\n");
  assert.equal(run(root).status, 1, "an explicit empty mapping uses engine defaults");
});

test("ambient rc and alternate config files cannot override the required YAML", (t) => {
  const root = fixture(t, { "a.md": "text" });
  put(root, ".markdownlintrc", '{"default":false}');
  put(root, ".markdownlint.json", '{"default":false}');
  assert.equal(run(root).status, 1);
});

test("a file deleted after selection is an engine read failure, not silently skipped", (t) => {
  const root = fixture(t, { "a.md": "text\n" });
  const files = markdownFiles(root);
  fs.unlinkSync(path.join(root, "a.md"));
  const previous = process.cwd();
  try {
    process.chdir(root);
    assert.throws(() => lintFiles(files), /ENOENT/);
    assert.throws(() => lintFiles(files, { fix: true }), /ENOENT/);
  } finally {
    process.chdir(previous);
  }
});

test("unreadable ignore file is not mistaken for no ignore file", (t) => {
  const root = fixture(t, { "a.md": "text\n" });
  fs.mkdirSync(path.join(root, ".markdownlintignore"));
  assert.equal(run(root, "--count-only").status, 4);
});

test("read, traversal and fix-write failures remain nonzero", { skip: process.platform === "win32" || process.getuid?.() === 0 }, (t) => {
  const root = fixture(t, { "a.md": "text", "private/b.md": "ok\n" });
  const file = path.join(root, "a.md");
  const directory = path.join(root, "private");
  try {
    fs.chmodSync(file, 0);
    assert.equal(run(root).status, 4);
    fs.chmodSync(file, 0o400);
    assert.equal(run(root, "--fix").status, 4);
    fs.chmodSync(file, 0o600);
    fs.chmodSync(directory, 0);
    assert.equal(run(root, "--count-only").status, 4);
  } finally {
    fs.chmodSync(file, 0o600);
    fs.chmodSync(directory, 0o700);
  }
  assert.equal(fs.readFileSync(file, "utf8"), "text");
});
