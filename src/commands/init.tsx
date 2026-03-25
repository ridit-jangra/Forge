import React, { useEffect, useState } from "react";
import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import { ACCENT, GREEN, RED, TEXT } from "../colors";
import { initRepo } from "../utils/repo";

export function InitCommand() {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const res = initRepo(".");
    if (res.error) setError(res.error);
    else setStage("done");

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
        <Box gap={1}>
          <Text color={ACCENT}>
            <Spinner type="point" />
          </Text>
          <Text>Init</Text>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>✓ Initialized an empty repo!</Text>
          <Text color={TEXT}>Start building!</Text>
        </Box>
      )}
    </>
  );
}
