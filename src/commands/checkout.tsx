import { Box, Text } from "ink";
import { ACCENT, GREEN, RED, TEXT } from "../colors";
import { useEffect, useState } from "react";
import Spinner from "ink-spinner";
import { checkoutCommit } from "../utils/checkout";

export function CheckoutCommand({ commitId }: { commitId: string }) {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const res = checkoutCommit(commitId, ".");
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
        <Text color={TEXT}>Retry</Text>
      </Box>
    );

  return (
    <>
      {stage === "working" && (
        <Box flexDirection="column">
          <Box gap={1}>
            <Text color={ACCENT}>
              <Spinner type="balloon" />
            </Text>
            <Text>Checking out</Text>
            <Text color={"gray"}>'{commitId}'</Text>
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>✓ Checkout {commitId}</Text>
        </Box>
      )}
    </>
  );
}
