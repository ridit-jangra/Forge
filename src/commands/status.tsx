import { Box, Text } from "ink";
import { ACCENT, BLUE, GREEN, PURPLE, RED, TEXT, YELLOW } from "../colors";
import { useEffect, useState } from "react";
import { listAllFilesWithStatus, type FileRef } from "../utils/status";
import Spinner from "ink-spinner";
import type { FileStatus } from "../types/files";

export function StatusCommand() {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);
  const [files, setFiles] = useState<FileRef[]>([]);

  useEffect(() => {
    const res = listAllFilesWithStatus(".");

    if (res.error) {
      setError(res.error);
      return;
    }
    if (!res.files) {
      setError("no files found.");
      return;
    }

    setFiles(res.files);

    setStage("done");
  }, []);

  const colorMap: Record<FileStatus, string> = {
    deleted: RED,
    modified: YELLOW,
    staged: BLUE,
    untracked: PURPLE,
    unchanged: TEXT,
  };

  if (error)
    return (
      <Box flexDirection="column">
        <Text color={RED}>✗ {error}</Text>
        <Text color={TEXT}>Retry</Text>
      </Box>
    );

  return (
    <>
      {stage === "working" && (
        <Box flexDirection="column">
          <Box gap={1}>
            <Text color={ACCENT}>
              <Spinner type="balloon2" />
            </Text>
            <Text>Fetching status</Text>
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>✓ Status</Text>
          {files.length > 0 ? (
            files.map((file) => (
              <Box key={file.path} flexDirection="column">
                <Box gap={1}>
                  <Text>{file.path}</Text>
                  <Text color={colorMap[file.status]}>({file.status})</Text>
                </Box>
              </Box>
            ))
          ) : (
            <Text color={TEXT}>No files found</Text>
          )}
        </Box>
      )}
    </>
  );
}
