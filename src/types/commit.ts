import type { FileBlob } from "./files";

export interface Commit {
  id: string;
  message: string;
  fileBlobs: FileBlob[];
  date: string;
}

export interface CommitRef {
  id: string;
  message: string;
  branch: string;
  date: string;
}
