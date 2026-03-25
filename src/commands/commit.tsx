import figures from "figures";
import { Box, Text } from "ink";
import { ACCENT, GREEN, RED, TEXT } from "../colors";
import { useEffect, useState } from "react";
import Spinner from "ink-spinner";
import { commit } from "../utils/commit";

export function CommitCommand({
  isAll,
  singlePath,
  message,
}: {
  isAll?: boolean;
  singlePath?: string;
  message: string;
}) {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAll && !singlePath) {
      setError("use -a / --all or specify path");
    }
  }, []);

  useEffect(() => {
    const res = commit(message, ".");
    if (res.error) {
      setError(res.error);
      return;
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
              <Spinner type="toggle10" />
            </Text>
            <Text>Commiting</Text>
          </Box>
          <Box gap={1}>
            <Text color={ACCENT}>{figures.arrowRight}</Text>
            <Text color={"gray"}>{message}</Text>
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>✓ Done</Text>
        </Box>
      )}
    </>
  );
}
