import { EventEmitter } from "events";
export const switchEmitter = new EventEmitter();

export type SwitchEvent =
  | { type: "checkpoint_created"; branch: string }
  | { type: "files_deleted"; files: string[] }
  | { type: "files_restored"; files: string[]; source: "checkpoint" | "commit" }
  | { type: "switched"; from: string; to: string };
