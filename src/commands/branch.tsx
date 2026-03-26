import { Box, Text } from "ink";
import { useEffect, useState } from "react";
import { ACCENT, GREEN, RED } from "../colors";
import Spinner from "ink-spinner";
import {
  createBranch,
  deleteBranch,
  mergeBranch,
  switchBranch,
} from "../utils/branch";
import { switchEmitter } from "../utils/switchEvents";
import type { SwitchEvent } from "../utils/switchEvents";

export function BranchCommand({
  name,
  isDelete,
  isSwitch,
  isMerge,
  mergingBranchName,
}: {
  name: string;
  isDelete?: boolean;
  isSwitch?: boolean;
  isMerge?: boolean;
  mergingBranchName?: string;
}) {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    switchEmitter.on("event", (e: SwitchEvent) => {
      if (e.type === "checkpoint_created")
        setLogs((l) => [...l, `📦 Checkpoint saved for ${e.branch}`]);
      if (e.type === "files_deleted")
        setLogs((l) => [...l, `🗑  Deleted ${e.files.length} files`]);
      if (e.type === "files_restored")
        setLogs((l) => [
          ...l,
          `✅ Restored ${e.files.length} files from ${e.source}`,
        ]);
      if (e.type === "switched")
        setLogs((l) => [...l, `⇒  ${e.from} → ${e.to}`]);
      if (e.type === "merge_conflict_detected")
        setLogs((l) => [...l, `⚠️  Conflict in: ${e.files.join(", ")}`]);
      if (e.type === "merge_complete")
        setLogs((l) => [
          ...l,
          `🔀 Merged ${e.from} → ${e.to} (${e.filesChanged} files changed)`,
        ]);
    });
    return () => {
      switchEmitter.removeAllListeners("event");
    };
  }, []);

  useEffect(() => {
    if (isSwitch) {
      const res = switchBranch(".", name);
      if (res.error) {
        setError(res.error);
        return;
      }
    } else if (isDelete) {
      const res = deleteBranch(".", name);
      if (res.error) {
        setError(res.error);
        return;
      }
    } else if (isMerge) {
      if (!mergingBranchName) {
        setError("specify target branch name.");
        return;
      }
      const res = mergeBranch(name, mergingBranchName, ".");
      if (res.error) {
        setError(res.error);
        return;
      }
    } else {
      const res = createBranch(".", name);
      if (res.error) {
        setError(res.error);
        return;
      }
    }
    setStage("done");
  }, []);

  if (error)
    return (
      <Box flexDirection="column">
        <Text color={RED}>✗ {error}</Text>
        {logs.map((log, i) => (
          <Text key={i} color="grey">
            {log}
          </Text>
        ))}
      </Box>
    );

  return (
    <>
      {stage === "working" && (
        <Box flexDirection="column">
          <Box gap={1}>
            <Text color={ACCENT}>
              <Spinner type="circleQuarters" />
            </Text>
            <Text>
              {isDelete
                ? "Deleting"
                : isSwitch
                  ? "Switching"
                  : isMerge
                    ? "Merging"
                    : "Creating"}{" "}
              branch
            </Text>
            <Text color={isDelete ? RED : GREEN}>{name}</Text>
            {isMerge && <Text>into</Text>}
            {isMerge && mergingBranchName && (
              <Text color={ACCENT}>{mergingBranchName}</Text>
            )}
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>
            ✓{" "}
            {isDelete
              ? "Deleted"
              : isSwitch
                ? "Switched"
                : isMerge
                  ? "Merged"
                  : "Created"}{" "}
            branch {name}
          </Text>
          {logs.map((log, i) => (
            <Text key={i} color="grey">
              {log}
            </Text>
          ))}
        </Box>
      )}
    </>
  );
}
