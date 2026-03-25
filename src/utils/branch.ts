import path from "path";
import fs from "fs";
import type { Branch } from "../types/branch";
import type { Repo } from "../types/repo";
import type { Commit } from "../types/commit";
import { matchPaths } from "./forgeIgnore";
import { createCheckpoint } from "./checkpoint";
import type { FileBlob } from "../types/files";
import { determineFileStatus } from "./add";
import { commitInBranch, getCommit, getLatestCommitId } from "./commit";
import { updateRepo } from "./repo";
import type { Checkpoint } from "../types/checkpoint";
import { switchEmitter } from "./switchEvents";

function getBranchPaths(repo_path: string, branch_name?: string) {
  const forgeFolder = path.join(repo_path, ".forge");
  const branchesFolder = path.join(forgeFolder, "branches");
  const branchFolder = branch_name
    ? path.join(branchesFolder, branch_name)
    : undefined;
  const branchDataFile = branchFolder
    ? path.join(branchFolder, "branch.json")
    : undefined;
  return { forgeFolder, branchesFolder, branchFolder, branchDataFile };
}

export function createBranch(
  repo_path: string,
  branch_name: string,
): { status: "ok" | "error"; error?: string } {
  const { branchDataFile, branchFolder, branchesFolder } = getBranchPaths(
    repo_path,
    branch_name,
  );
  const branchCommitsFolder = path.join(branchFolder!, "commits");

  if (!fs.existsSync(branchesFolder))
    fs.mkdirSync(branchesFolder, { recursive: true });

  try {
    fs.mkdirSync(branchFolder!, { recursive: true });
    fs.mkdirSync(branchCommitsFolder, { recursive: true });

    fs.writeFileSync(
      branchDataFile!,
      JSON.stringify({ name: branch_name, latestCommitId: "" } as Branch),
    );

    commitInBranch("Initial commit", repo_path, branch_name);
  } catch (err) {
    return { status: "error", error: err as string };
  }

  return { status: "ok" };
}

export function getBranch(
  repo_path: string,
  branch_name: string,
): { status: "ok" | "error"; branch?: Branch; error?: string } {
  const { branchDataFile, branchFolder, branchesFolder } = getBranchPaths(
    repo_path,
    branch_name,
  );

  if (!fs.existsSync(branchesFolder))
    return {
      status: "error",
      error: "branches folder is missing, consider reinitialize repo.",
    };

  if (!fs.existsSync(branchFolder!))
    return {
      status: "error",
      error: `${branch_name} doesn't exists.`,
    };

  if (!fs.existsSync(branchDataFile!))
    return {
      status: "error",
      error: `${branch_name} meta data is missing, consider reinitialize the branch.`,
    };

  const branchData = JSON.parse(fs.readFileSync(branchDataFile!, "utf-8"));

  return { status: "ok", branch: branchData };
}

export function updateBranch(
  repo_path: string,
  branch_name: string,
  latest_commit_id: string,
): { status: "ok" | "error"; error?: string } {
  const { branchDataFile, branchFolder, branchesFolder } = getBranchPaths(
    repo_path,
    branch_name,
  );

  if (!fs.existsSync(branchesFolder))
    return {
      status: "error",
      error: "branches folder is missing, consider reinitialize repo.",
    };

  if (!fs.existsSync(branchFolder!))
    return {
      status: "error",
      error: `${branch_name} doesn't exists.`,
    };

  if (!fs.existsSync(branchDataFile!))
    return {
      status: "error",
      error: `${branch_name} meta data is missing, consider reinitialize the branch.`,
    };

  const branchData = JSON.parse(
    fs.readFileSync(branchDataFile!, "utf-8"),
  ) as Branch;
  const newData = { ...branchData, latestCommitId: latest_commit_id } as Branch;

  fs.writeFileSync(branchDataFile!, JSON.stringify(newData));

  return { status: "ok" };
}

export function getCurrentBranch(repo_path: string): {
  status: "ok" | "error";
  branch?: Branch;
  error?: string;
} {
  const { branchesFolder } = getBranchPaths(repo_path);
  const forgeFolder = path.join(repo_path, ".forge");
  const repoDataFile = path.join(forgeFolder, "repo.json");

  if (!fs.existsSync(branchesFolder))
    return {
      status: "error",
      error: "branches folder is missing, consider reinitialize repo.",
    };

  if (!fs.existsSync(repoDataFile))
    return {
      status: "error",
      error: `repo meta data is missing, consider reinitialize the branch.`,
    };

  const branchName = (
    JSON.parse(fs.readFileSync(repoDataFile, "utf-8")) as Repo
  ).branch;

  const branchFolder = path.join(branchesFolder, branchName);
  const branchDataFile = path.join(branchFolder, "branch.json");

  if (!fs.existsSync(branchFolder))
    return {
      status: "error",
      error: `${branchName} doesn't exists, consider reinitializing the repo.`,
    };

  if (!fs.existsSync(branchDataFile))
    return {
      status: "error",
      error: `${branchName} meta data is missing, consider reinitialize the branch.`,
    };

  const branchData = JSON.parse(
    fs.readFileSync(branchDataFile, "utf-8"),
  ) as Branch;

  return { status: "ok", branch: branchData };
}

export function listBranches(repo_path: string): {
  status: "ok" | "error";
  branches?: Branch[];
  error?: string;
} {
  const { branchesFolder } = getBranchPaths(repo_path);

  if (!fs.existsSync(branchesFolder))
    return {
      status: "error",
      error: "branches folder is missing, consider reinitialize repo.",
    };

  const files = fs.readdirSync(branchesFolder);
  const branches = files.map((file) => {
    const branch = JSON.parse(
      fs.readFileSync(
        path.join(branchesFolder, file.toString(), "branch.json"),
        "utf-8",
      ),
    ) as Branch;
    return branch;
  });

  return { status: "ok", branches };
}

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

export function switchBranch(
  repo_path: string,
  branch_name: string,
): { status: "ok" | "error"; error?: string } {
  const currentBranch = getCurrentBranch(repo_path);
  if (currentBranch.error || !currentBranch.branch)
    return { status: "error", error: "no current branch found" };

  const list = fs.readdirSync(".", { recursive: true });
  const files = processFiles(".", list);

  const latestCommitId = getLatestCommitId(
    repo_path,
    currentBranch.branch.name,
  );
  if (latestCommitId.error)
    return { status: "error", error: latestCommitId.error };

  const fileBlobs = files.files?.map((f) => ({
    name: path.basename(f),
    path: f,
    content: fs.readFileSync(f, "utf-8").toString(),
    status: determineFileStatus(repo_path, f).file_status ?? "untracked",
  })) as FileBlob[];

  const res = createCheckpoint(
    repo_path,
    fileBlobs,
    currentBranch.branch.name,
    latestCommitId.latestCommitId ?? "",
  );
  if (res.error) return { status: "error", error: res.error };
  switchEmitter.emit("event", {
    type: "checkpoint_created",
    branch: currentBranch.branch.name,
  });

  files.files?.forEach((f) => fs.rmSync(f, { recursive: true }));
  switchEmitter.emit("event", {
    type: "files_deleted",
    files: files.files ?? [],
  });

  const newBranch = getBranch(repo_path, branch_name);
  if (newBranch.error || !newBranch.branch)
    return {
      status: "error",
      error: newBranch.error || `${branch_name} not found`,
    };

  const latestCommit = newBranch.branch.latestCommitId
    ? getCommit(repo_path, newBranch.branch.latestCommitId, branch_name)
    : null;
  if (latestCommit?.error)
    return { status: "error", error: latestCommit.error };

  const checkpointFile = path.join(
    repo_path,
    ".forge",
    "branches",
    branch_name,
    "checkpoint.json",
  );
  const hasCheckpoint = fs.existsSync(checkpointFile);

  if (hasCheckpoint) {
    const checkpointData = JSON.parse(
      fs.readFileSync(checkpointFile, "utf-8"),
    ) as Checkpoint;
    const targetLatestCommitId = getLatestCommitId(repo_path, branch_name);

    const checkpointIsLatest =
      targetLatestCommitId.latestCommitId === checkpointData.commitId ||
      new Date(checkpointData.date) >=
        new Date(latestCommit?.commit?.date ?? 0);

    if (checkpointIsLatest) {
      checkpointData.files.forEach((file) =>
        fs.writeFileSync(file.path, file.content),
      );
      switchEmitter.emit("event", {
        type: "files_restored",
        files: checkpointData.files.map((f) => f.path),
        source: "checkpoint",
      });
    } else {
      latestCommit?.commit?.fileBlobs.forEach((file) =>
        fs.writeFileSync(file.path, file.content),
      );
      switchEmitter.emit("event", {
        type: "files_restored",
        files: latestCommit?.commit?.fileBlobs.map((f) => f.path) ?? [],
        source: "commit",
      });
    }
  } else {
    latestCommit?.commit?.fileBlobs.forEach((file) =>
      fs.writeFileSync(file.path, file.content),
    );
    switchEmitter.emit("event", {
      type: "files_restored",
      files: latestCommit?.commit?.fileBlobs.map((f) => f.path) ?? [],
      source: "commit",
    });
  }

  const res_2 = updateRepo(repo_path, { branch: branch_name });
  if (res_2.error) return { status: "error", error: res_2.error };

  switchEmitter.emit("event", {
    type: "switched",
    from: currentBranch.branch.name,
    to: branch_name,
  });

  return { status: "ok" };
}
