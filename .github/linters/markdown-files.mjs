// Fixed repository selection, not a glob implementation. See ADR-0005.
import fs from "node:fs";
import path from "node:path";
import ignore from "ignore";

const rootExclusions = [
  "node_modules", ".github/linters/node_modules", "CHANGELOG.md", "MIGRATION.md",
];

export function markdownFiles(cwd = process.cwd(), platform = process.platform) {
  const root = path.resolve(cwd);
  const realRoot = fs.realpathSync(root);
  const foldExtension = platform === "darwin" || platform === "win32";
  const directories = new Set();
  for (const name of rootExclusions) {
    try {
      // The CLI's lstat distinguishes a directory from a symlink to one.
      if (fs.lstatSync(path.join(root, name)).isDirectory()) directories.add(name);
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  const ignored = ignore();
  const ignorePath = path.join(root, ".markdownlintignore");
  try {
    fs.lstatSync(ignorePath);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    return enumerate();
  }
  ignored.add(fs.readFileSync(ignorePath, "utf8"));
  return enumerate();

  function excluded(relative) {
    // These are literal, root-relative exclusions, NOT gitignore patterns.
    return rootExclusions.includes(relative) ||
      [...directories].some((directory) => relative.startsWith(`${directory}/`));
  }

  function enumerate() {
    const files = [];
    function walk(directory, prefix, ancestors) {
      const real = fs.realpathSync(directory);
      const outside = path.relative(realRoot, real);
      if (outside === ".." || outside.startsWith(`..${path.sep}`) || path.isAbsolute(outside)) {
        throw new Error(`Markdown traversal escapes repository: ${prefix}`);
      }
      if (ancestors.has(real)) throw new Error(`Markdown symlink cycle: ${prefix}`);
      // Branch-local ancestry keeps legitimate lexical aliases to one target.
      const branch = new Set([...ancestors, real]);
      const entries = fs.readdirSync(directory, { withFileTypes: true });
      entries.sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
      for (const entry of entries) {
        const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
        const absolute = path.join(directory, entry.name);
        // A fixed exclusion that names a symlink is an exact-file exclusion,
        // not a directory exclusion; its descendants must still be traversed.
        if (directories.has(relative)) continue;
        let info = entry;
        if (entry.isSymbolicLink()) {
          const target = fs.realpathSync(absolute);
          const outside = path.relative(realRoot, target);
          if (outside === ".." || outside.startsWith(`..${path.sep}`) || path.isAbsolute(outside)) {
            throw new Error(`Markdown symlink escapes repository: ${relative}`);
          }
          info = fs.statSync(absolute);
        }
        if (info.isDirectory()) {
          walk(absolute, relative, branch);
        } else {
          const name = foldExtension ? entry.name.toLowerCase() : entry.name;
          if (name.endsWith(".md") && !excluded(relative) && !ignored.ignores(relative)) {
            if (!info.isFile()) throw new Error(`Not a regular Markdown file: ${relative}`);
            files.push(relative);
          }
        }
      }
    }
    walk(root, "", new Set());
    return files.sort();
  }
}
