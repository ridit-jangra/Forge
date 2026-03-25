import path from "path";
import fs from "fs";
import type { FileBlob } from "../types/repo";

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

  const tempFiles: string[] = Array.isArray(parsed.files) ? parsed.files : [];

  const alreadyExists = tempFiles.some((f: any) => f.path === file_path);

  if (alreadyExists) {
    return { status: "ok" };
  }

  const newTempFiles = [
    ...tempFiles,
    {
      name: path.basename(file_path),
      path: file_path,
      content: fs.readFileSync(file_path).toString(),
    } as FileBlob,
  ];

  fs.writeFileSync(
    tempAddedFiles,
    JSON.stringify({ files: newTempFiles }, null, 2),
  );

  return { status: "ok" };
}
