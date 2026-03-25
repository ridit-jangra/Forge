import path from "path";
import fs from "fs";
import type { Checkpoint } from "../types/checkpoint";
import type { FileBlob } from "../types/files";

export function createCheckpoint(
  repo_path: string,
  fileBlobs: FileBlob[],
  branch_name: string,
  commitId: string,
): { status: "ok" | "error"; error?: string } {
  const forgeFolder = path.join(repo_path, ".forge");
  const checkpointsFolder = path.join(forgeFolder, "branches", branch_name);
  [];

  if (!fs.existsSync(checkpointsFolder))
    fs.mkdirSync(checkpointsFolder, { recursive: true });

  const checkpointData = {
    date: new Date().toISOString(),
    files: fileBlobs,
  } as Checkpoint;

  const checkpointFile = path.join(checkpointsFolder, "checkpoint.json");
  fs.writeFileSync(checkpointFile, JSON.stringify(checkpointData));

  return { status: "ok" };
}

export function getCheckpoint(
  repo_path: string,
  branch_name: string,
): { status: "ok" | "error"; checkpoint?: Checkpoint; error?: string } {
  const forgeFolder = path.join(repo_path, ".forge");
  const checkpointsFolder = path.join(forgeFolder, "branches", branch_name);

  if (!fs.existsSync(checkpointsFolder))
    return {
      status: "error",
      error: "checkpoints folder is missing, consider reinitializing repo.",
    };

  const checkpointsFile = path.join(checkpointsFolder, "checkpoint.json");
  if (!fs.existsSync(checkpointsFile))
    return { status: "error", error: `checkpoint doesn't exists.` };

  const checkpointData = JSON.parse(
    fs.readFileSync(checkpointsFile, "utf-8"),
  ) as Checkpoint;

  return { status: "ok", checkpoint: checkpointData };
}
