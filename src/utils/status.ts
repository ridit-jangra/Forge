import { matchPaths } from "./forgeIgnore";
import path from "path";
import fs from "fs";
import type { FileStatus } from "../types/files";
import { checkPrime } from "crypto";
import { determineFileStatus } from "./add";

function processFiles(basePath: string, files: (string | Buffer)[]) {
  const normalized = files
    .map((f) => path.join(basePath, f.toString()).replace(/\\/g, "/"))
    .filter((p) => {
      try {
        return fs.statSync(p).isFile();
      } catch {
        return false;
      }
    });

  const checkedFiles = matchPaths(normalized);

  return checkedFiles;
}

export interface FileRef {
  path: string;
  status: FileStatus;
}

export function listAllFilesWithStatus(repo_path: string): {
  status: "error" | "ok";
  error?: string;
  files?: FileRef[];
} {
  const list = fs.readdirSync(".", { recursive: true });
  const checkedFiles = processFiles(".", list);

  let files: { path: string; status: FileStatus }[] = [];

  checkedFiles.files?.forEach((file) => {
    const status =
      determineFileStatus(repo_path, file).file_status ?? "unchanged";
    files.push({ path: file, status });
  });

  return { status: "ok", files: files.filter((f) => f.status !== "unchanged") };
}
