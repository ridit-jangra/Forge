import { Box, Text } from "ink";
import { useEffect, useState } from "react";
import { ACCENT, GREEN, RED } from "../colors";
import Spinner from "ink-spinner";
import { createBranch, switchBranch } from "../utils/branch";
import { switchEmitter } from "../utils/switchEvents";
import type { SwitchEvent } from "../utils/switchEvents";

export function BranchCommand({
  name,
  isDelete,
  isSwitch,
}: {
  name: string;
  isDelete?: boolean;
  isSwitch?: boolean;
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
              {isDelete ? "Deleting" : isSwitch ? "Switching" : "Creating"}{" "}
              branch
            </Text>
            <Text color={isDelete ? RED : GREEN}>{name}</Text>
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>
            ✓ {isDelete ? "Deleted" : isSwitch ? "Switched" : "Created"} branch{" "}
            {name}
          </Text>
          {logs.map((log, i) => (
            <Text key={i} color={"grey"}>
              {log}
            </Text>
          ))}
        </Box>
      )}
    </>
  );
}
