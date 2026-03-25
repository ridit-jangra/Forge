import path from "path";
import fs from "fs";
import type { Commit } from "../types/commit";
import type { FileBlob } from "../types/repo";

export function commit(
  message: string,
  repo_path: string,
): {
  status: "ok" | "error";
  error?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const commitFolder = path.join(forgeFolder, "commits");
  const tempAddedFiles = path.join(forgeFolder, "tempAddedFiles.json");

  if (!fs.existsSync(tempAddedFiles))
    return {
      status: "error",
      error: "tempAddedFiles.json is missing, consider reinitialize repo.",
    };

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  const parsed = JSON.parse(fs.readFileSync(tempAddedFiles, "utf-8"));

  const tempFiles: FileBlob[] = Array.isArray(parsed.files) ? parsed.files : [];

  const fileBlobs = tempFiles;

  const newCommitId = crypto.randomUUID();
  const newCommit: Commit = {
    id: newCommitId,
    message: message,
    fileBlobs,
  };

  fs.writeFileSync(
    path.join(commitFolder, `${newCommitId}.json`),
    JSON.stringify(newCommit),
  );

  fs.writeFileSync(tempAddedFiles, JSON.stringify({ files: [] }));

  return { status: "ok" };
}

export function logCommits(repo_path: string): {
  status: "ok" | "error";
  error?: string;
  commits?: string[];
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const commitFolder = path.join(forgeFolder, "commits");

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  const files = fs.readdirSync(commitFolder, { recursive: true });
  const commits = files.map((file) => path.basename(file.toString(), ".json"));

  return { status: "ok", commits };
}
