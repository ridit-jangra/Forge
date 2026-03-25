import { Box, Text } from "ink";
import { ACCENT, GREEN, RED, TEXT } from "../colors";
import { useEffect, useState } from "react";
import Spinner from "ink-spinner";
import { logCommits } from "../utils/commit";

export function LogCommand() {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);
  const [commits, setCommits] = useState<string[]>([]);

  useEffect(() => {
    const res = logCommits(".");
    if (res.error) {
      setError(res.error);
      return;
    }
    if (!res.commits) setCommits([]);
    else setCommits(res.commits);
    setStage("done");
  }, []);

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
              <Spinner type="circleHalves" />
            </Text>
            <Text>Logging</Text>
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>✓ Logs</Text>
          {commits.length > 0 ? (
            commits.map((commit) => (
              <Text color={"gray"} key={commit}>
                {commit}
              </Text>
            ))
          ) : (
            <Text color={TEXT}>No commits found</Text>
          )}
        </Box>
      )}
    </>
  );
}
