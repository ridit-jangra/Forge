import type { FileBlob } from "./repo";

export interface Commit {
  id: string;
  message: string;
  fileBlobs: FileBlob[];
}
