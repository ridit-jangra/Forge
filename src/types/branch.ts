import type { Commit } from "./commit";

export interface Branch {
  name: string;
  latestCommitId: string;
}
