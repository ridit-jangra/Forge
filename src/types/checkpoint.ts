import type { FileBlob } from "./files";

export interface Checkpoint {
  files: FileBlob[];
  date: string;
  commitId: string;
}
