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
  else {
    return {
      status: "error",
      error: "Consider making .forgeignore or .gitignore",
    };
  }

  const content = fs.readFileSync(ignoreFile, "utf-8");
  ig.add(content);

  ig.add(".git");

  const checkedFiles: string[] = [];

  files.forEach((file) => {
    if (!ig.ignores(file)) checkedFiles.push(file);
  });

  return { status: "ok", files: checkedFiles };
}
