import crypto from "crypto";
import path from "path";
import fs from "fs";

export function hashContent(content: string): string {
  return crypto.createHash("sha256").update(content).digest("hex");
}

export function writeObject(repo_path: string, content: string): string {
  const hash = hashContent(content);
  const folder = hash.slice(0, 2);
  const file = hash.slice(2);

  const objectDir = path.join(repo_path, ".forge", "objects", folder);
  const objectPath = path.join(objectDir, file);

  if (!fs.existsSync(objectDir)) fs.mkdirSync(objectDir, { recursive: true });
  if (!fs.existsSync(objectPath)) fs.writeFileSync(objectPath, content);

  return hash;
}

export function readObject(repo_path: string, hash: string): string {
  const folder = hash.slice(0, 2);
  const file = hash.slice(2);
  const objectPath = path.join(repo_path, ".forge", "objects", folder, file);
  return fs.readFileSync(objectPath, "utf-8");
}
