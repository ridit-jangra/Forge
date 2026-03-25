import type { Commit } from "./commit";

export type UnstagedFileStatus = "deleted" | "untracked" | "modified";

export interface Repo {
  name: string;
  commits: Commit[];
  isFork: boolean;
}

export interface FileBlob {
  name: string;
  path: string;
  content: string;
}
