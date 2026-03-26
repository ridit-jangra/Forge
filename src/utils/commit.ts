import path from "path";
import fs from "fs";
import type { Commit, CommitRef } from "../types/commit";
import type { FileBlob } from "../types/files";
import { updateBranch } from "./branch";
import type { Repo } from "../types/repo";
import type { Branch } from "../types/branch";

export function commitInGlobal(
  message: string,
  repo_path: string,
  branch_name: string,
  commitId: string,
): {
  status: "ok" | "error";
  error?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const commitFolder = path.join(forgeFolder, "commits");

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  const newCommit: CommitRef = {
    id: commitId,
    message: message,
    date: new Date().toISOString(),
    branch: branch_name,
  };

  fs.writeFileSync(
    path.join(commitFolder, `${commitId}.json`),
    JSON.stringify(newCommit),
  );

  return { status: "ok" };
}

export function commitInBranch(
  message: string,
  repo_path: string,
  branch_name: string,
): {
  status: "ok" | "error";
  error?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const branchesFolder = path.join(forgeFolder, "branches");
  const branchFolder = path.join(branchesFolder, branch_name);
  const commitFolder = path.join(branchFolder, "commits");
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

  let parentCommit;

  const latestCommitId = getLatestCommitId(repo_path, branch_name);
  if (latestCommitId.error || !latestCommitId.latestCommitId) {
  } else {
    parentCommit = latestCommitId.latestCommitId;
  }

  const newCommitId = crypto.randomUUID();
  const newCommit: Commit = {
    id: newCommitId,
    message: message,
    fileBlobs,
    date: new Date().toISOString(),
    parent: parentCommit,
  };

  fs.writeFileSync(
    path.join(commitFolder, `${newCommitId}.json`),
    JSON.stringify(newCommit),
  );

  fs.writeFileSync(tempAddedFiles, JSON.stringify({ files: [] }));

  const res = updateBranch(repo_path, branch_name, newCommitId);
  if (res.error) return { status: "error", error: res.error };

  commitInGlobal(message, repo_path, branch_name, newCommitId);

  return { status: "ok" };
}

export function logCommits(repo_path: string): {
  status: "ok" | "error";
  error?: string;
  commits?: CommitRef[];
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const commitFolder = path.join(forgeFolder, "commits");

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  const files = fs.readdirSync(commitFolder);
  const commits = files.map((file) => {
    const commit = JSON.parse(
      fs.readFileSync(path.join(commitFolder, file.toString()), "utf-8"),
    ) as CommitRef;
    return commit;
  });

  return { status: "ok", commits };
}

export function logCommitsInBranch(
  repo_path: string,
  branch_name: string,
): {
  status: "ok" | "error";
  error?: string;
  commits?: Commit[];
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const branchesFolder = path.join(forgeFolder, "branches");
  const branchFolder = path.join(branchesFolder, branch_name);
  const commitFolder = path.join(branchFolder, "commits");

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  const files = fs.readdirSync(commitFolder);
  const commits = files.map((file) => {
    const commit = JSON.parse(
      fs.readFileSync(path.join(commitFolder, file.toString()), "utf-8"),
    ) as Commit;
    return commit;
  });

  return { status: "ok", commits };
}

export function getCommit(
  repo_path: string,
  commitId: string,
  branch_name: string,
): {
  status: "ok" | "error";
  error?: string;
  commit?: Commit;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const commitFolder = path.join(
    forgeFolder,
    "branches",
    branch_name,
    "commits",
  );

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  const commitFile = path.join(commitFolder, `${commitId}.json`);

  if (!fs.existsSync(commitFile))
    return {
      status: "error",
      error: `${commitId} doesn't exists.`,
    };

  const commitData = JSON.parse(fs.readFileSync(commitFile, "utf-8")) as Commit;

  return { status: "ok", commit: commitData };
}

export function getLatestCommitId(
  repo_path: string,
  branch_name?: string,
): {
  status: "ok" | "error";
  error?: string;
  latestCommitId?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const repoDataFile = path.join(forgeFolder, "repo.json");

  if (!fs.existsSync(repoDataFile))
    return {
      status: "error",
      error: `repo meta data is missing, consider reinitialize the branch.`,
    };

  const repoData = JSON.parse(fs.readFileSync(repoDataFile, "utf-8")) as Repo;
  const branchName = branch_name ?? repoData.branch;
  const branchFolder = path.join(forgeFolder, "branches", branchName);

  if (!fs.existsSync(branchFolder))
    return {
      status: "error",
      error: `${branchName} doesn't exists, consider reinitializing the repo.`,
    };

  const branchDataFile = path.join(branchFolder, "branch.json");

  if (!fs.existsSync(branchDataFile))
    return {
      status: "error",
      error: `${branchName} meta data is missing, consider reinitialize the branch.`,
    };

  const branchData = JSON.parse(
    fs.readFileSync(branchDataFile, "utf-8"),
  ) as Branch;

  return { status: "ok", latestCommitId: branchData.latestCommitId };
}
