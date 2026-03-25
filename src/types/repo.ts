export type UnstagedFileStatus = "deleted" | "untracked" | "modified";

export interface Repo {
  name: string;
  commits: Commit[];
  isFork: boolean;
}

export interface FileBlob {
  name: string;
  path: string;
  history: { commit: string; content: string };
}

export interface UnstagedFile {
  status: UnstagedFile;
  content: string;
  name: string;
}

export interface Commit {
  id: string;
  fileBlobs: FileBlob[];
}
