import path from "path";
import fs from "fs";
import type { Repo } from "../types/repo";

export function initRepo(folder_path: string): {
  status: "ok" | "error";
  error?: string;
} {
  const cwd = folder_path;
  const forgeFolder = path.join(cwd, ".forge");
  const repoInfoFile = path.join(forgeFolder, "repo.json");
  const commitsFolder = path.join(forgeFolder, "commits");

  if (fs.existsSync(forgeFolder)) {
    return { status: "error", error: "Repo already exists" };
  }

  fs.mkdirSync(forgeFolder, { recursive: true });

  fs.writeFileSync(
    repoInfoFile,
    JSON.stringify({
      name: path.basename(folder_path),
      commits: [],
      isFork: false,
    } as Repo),
  );

  fs.mkdirSync(commitsFolder, { recursive: true });

  return { status: "ok" };
}
