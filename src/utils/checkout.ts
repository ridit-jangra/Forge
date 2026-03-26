import path from "path";
import fs from "fs";
import type { Commit } from "../types/commit";
import { getCurrentBranch } from "./branch";
import { readObject } from "./objects";

export function checkoutCommit(
  commitId: string,
  repo_path: string,
  branch_name?: string,
): {
  status: "ok" | "error";
  error?: string;
} {
  const forgeFolder = path.join(repo_path, ".forge");
  const currentBranch = getCurrentBranch(repo_path);
  if (currentBranch.error || !currentBranch.branch) {
    return {
      status: "error",
      error: currentBranch.error || "no current branch found.",
    };
  }
  const branchName = branch_name ?? currentBranch.branch.name;
  const commitFolder = path.join(
    forgeFolder,
    "branches",
    branchName,
    "commits",
  );
  const commitFile = path.join(commitFolder, `${commitId}.json`);

  if (!fs.existsSync(commitFolder))
    return {
      status: "error",
      error: "commits folder is missing, consider reinitialize repo.",
    };

  if (!fs.existsSync(commitFile))
    return {
      status: "error",
      error: "commit not found.",
    };

  const commitData: Commit = JSON.parse(fs.readFileSync(commitFile, "utf-8"));
  const files = commitData.fileBlobs;

  console.log(
    "restoring files:",
    files.map((f) => f.path),
  );

  files.forEach((file) => {
    fs.writeFileSync(file.path, readObject(repo_path, file.hash));
  });

  return { status: "ok" };
}
