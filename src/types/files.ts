export type FileStatus =
  | "deleted"
  | "untracked"
  | "modified"
  | "staged"
  | "unchanged";

export interface FileBlob {
  name: string;
  path: string;
  hash: string;
  status: FileStatus;
}
