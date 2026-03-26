import fs from "fs";
import ignore from "ignore";
import path from "path";

const ig = ignore({ allowRelativePaths: true });

export function matchPaths(files: string[]): {
  status: "ok" | "error";
  files?: string[];
  error?: string;
} {
  let ignoreFile;

  const forgeignoreFile = path.join(".", ".forgeignore");
  const gitignoreFile = path.join(".", ".gitignore");

  if (!fs.existsSync(forgeignoreFile)) ignoreFile = gitignoreFile;
  else if (fs.existsSync(forgeignoreFile)) ignoreFile = forgeignoreFile;

  if (ignoreFile && fs.existsSync(ignoreFile)) {
    const content = fs.readFileSync(ignoreFile, "utf-8");
    ig.add(content);
  }

  ig.add(".git");
  ig.add(".forge");
  ig.add("node_modules");

  const checkedFiles: string[] = [];

  files.forEach((file) => {
    if (!ig.ignores(file)) checkedFiles.push(file);
  });

  return { status: "ok", files: checkedFiles };
}

export function createDefaultForgeIgnore(repo_path: string): {
  status: "ok" | "error";
  error?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");

  if (!fs.existsSync(forgeFolder))
    return { status: "error", error: "repo doesn't exists" };

  const forgeignoreFile = path.join(repo_path, ".forgeignore");

  if (!fs.existsSync(forgeignoreFile))
    fs.writeFileSync(
      forgeignoreFile,
      "node_modules\n.git\nout\ndist\n.forge\.next\.cache\nbuild\n__pycache__\n.env\.DS_Store",
    );

  return { status: "ok" };
}
