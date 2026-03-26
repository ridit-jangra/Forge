import path from "path";
import fs from "fs";
import type { FileBlob, FileStatus } from "../types/files";
import { getCommit, getLatestCommitId } from "./commit";
import { getCurrentBranch } from "./branch";
import { hashContent, readObject, writeObject } from "./objects";

export function addFile(
  file_path: string,
  repo_path: string,
): {
  status: "ok" | "error";
  error?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const tempAddedFiles = path.join(forgeFolder, "tempAddedFiles.json");

  if (!fs.existsSync(tempAddedFiles))
    return {
      status: "error",
      error: "tempAddedFiles.json is missing, consider reinitialize repo.",
    };

  const parsed = JSON.parse(fs.readFileSync(tempAddedFiles, "utf-8"));

  const tempFiles: FileBlob[] = Array.isArray(parsed.files) ? parsed.files : [];

  const alreadyExists = tempFiles.some((f) => f.path === file_path);

  if (alreadyExists) {
    return { status: "ok" };
  }

  let fileStatus = determineFileStatus(repo_path, file_path);

  const content = fs.readFileSync(file_path).toString();
  const hash = writeObject(repo_path, content);

  const newTempFiles = [
    ...tempFiles,
    {
      name: path.basename(file_path),
      path: file_path,
      hash: hash,
      status: fileStatus.file_status ?? "untracked",
    } as FileBlob,
  ];

  fs.writeFileSync(
    tempAddedFiles,
    JSON.stringify({ files: newTempFiles }, null, 2),
  );

  return { status: "ok" };
}

export function determineFileStatus(
  repo_path: string,
  file_path: string,
): { status: "ok" | "error"; file_status?: FileStatus; error?: string } {
  const isInDisk = fs.existsSync(file_path);
  if (!isInDisk) return { status: "ok", file_status: "deleted" };

  const diskFileContent = fs.readFileSync(file_path).toString();

  const forgeFolder = path.join(repo_path, ".forge");
  const tempAddedFiles = path.join(forgeFolder, "tempAddedFiles.json");
  const latestCommitId = getLatestCommitId(repo_path);
  if (latestCommitId.error) {
    return {
      status: "error",
      error: latestCommitId.error,
    };
  }

  if (!latestCommitId.latestCommitId) {
    return { status: "ok", file_status: "untracked" };
  }

  const branchName = getCurrentBranch(repo_path);
  if (branchName.error || !branchName.branch) {
    return {
      status: "error",
      error: latestCommitId.error || "found no branch",
    };
  }

  const commitData = getCommit(
    repo_path,
    latestCommitId.latestCommitId,
    branchName.branch.name,
  );
  if (commitData.error || !commitData.commit) {
    return {
      status: "error",
      error: latestCommitId.error || "No commit data found.",
    };
  }

  const parsed = JSON.parse(fs.readFileSync(tempAddedFiles, "utf-8"));

  const tempFiles: FileBlob[] = Array.isArray(parsed.files) ? parsed.files : [];
  const commitFiles: FileBlob[] = commitData.commit.fileBlobs;

  const targetTempFile = tempFiles.find((t) => t.path === file_path);
  const targetComittedFile = commitFiles.find((c) => c.path === file_path);

  if (
    targetComittedFile &&
    isInDisk &&
    readObject(repo_path, targetComittedFile.hash) !== diskFileContent
  )
    return { status: "ok", file_status: "modified" };
  else if (
    targetComittedFile &&
    isInDisk &&
    readObject(repo_path, targetComittedFile.hash) === diskFileContent
  )
    return { status: "ok", file_status: "unchanged" };
  else if (!targetComittedFile && targetTempFile)
    return { status: "ok", file_status: "staged" };
  else if (!targetComittedFile && !targetTempFile)
    return { status: "ok", file_status: "untracked" };

  return { status: "ok" };
}
