import path from "path";
import fs from "fs";
import type { Repo } from "../types/repo";
import { createBranch } from "./branch";
import { createDefaultForgeIgnore } from "./forgeIgnore";

export function initRepo(folder_path: string): {
  status: "ok" | "error";
  error?: string;
} {
  const cwd = folder_path;
  const forgeFolder = path.join(cwd, ".forge");
  const repoInfoFile = path.join(forgeFolder, "repo.json");
  const tempAddedFiles = path.join(forgeFolder, "tempAddedFiles.json");
  const commitsFolder = path.join(forgeFolder, "commits");

  if (fs.existsSync(forgeFolder)) {
    return { status: "error", error: "Repo already exists" };
  }

  fs.mkdirSync(forgeFolder, { recursive: true });

  fs.writeFileSync(
    repoInfoFile,
    JSON.stringify({
      name: path.basename(folder_path),
      isFork: false,
      branch: "main",
    } as Repo),
  );

  fs.writeFileSync(tempAddedFiles, JSON.stringify({ files: [] }));

  fs.mkdirSync(commitsFolder, { recursive: true });

  const res = createBranch(".", "main");
  if (res.error) return { status: "error", error: res.error };

  const res_2 = createDefaultForgeIgnore(folder_path);
  if (res_2.error) return { status: "error", error: res_2.error };

  return { status: "ok" };
}

export function updateRepo(
  repo_path: string,
  data: Partial<Repo>,
): { status: "ok" | "error"; error?: string } {
  const forgeFolder = path.join(repo_path, ".forge");
  const repoInfoFile = path.join(forgeFolder, "repo.json");

  if (!fs.existsSync(repoInfoFile))
    return {
      status: "error",
      error: "repo.json is missing, consider reinitialize repo.",
    };

  const current = JSON.parse(fs.readFileSync(repoInfoFile, "utf-8")) as Repo;
  fs.writeFileSync(repoInfoFile, JSON.stringify({ ...current, ...data }));

  return { status: "ok" };
}
