import { Box, Text } from "ink";
import { ACCENT, GREEN, RED, TEXT } from "../colors";
import { useEffect, useState } from "react";
import { logCommits, logCommitsInBranch } from "../utils/commit";
import type { Commit, CommitRef } from "../types/commit";
import Spinner from "ink-spinner";
import { getCurrentBranch } from "../utils/branch";
import type { Branch } from "../types/branch";

export function LogCommand({ global }: { global?: boolean }) {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);
  const [commits, setCommits] = useState<Commit[] | CommitRef[]>([]);
  const [branch, setBranch] = useState<Branch | null>(null);

  useEffect(() => {
    const branch = getCurrentBranch(".");

    if (branch.error) {
      setError(branch.error);
      return;
    }
    if (!branch.branch) {
      setError("no branch found.");
      return;
    }

    setBranch(branch.branch);
  }, []);

  useEffect(() => {
    let res;

    if (global) {
      res = logCommits(".");
    } else {
      if (!branch) return;
      res = logCommitsInBranch(".", branch.name);
    }

    if (!res) return;

    if (res.error) {
      setError(res.error);
      return;
    }
    if (!res.commits) setCommits([]);
    else setCommits(res.commits);
    setStage("done");
  }, [branch]);

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
              <Box key={commit.id} flexDirection="column">
                <Box gap={1}>
                  <Text color={ACCENT}>commit</Text>
                  <Text>{commit.id}</Text>
                  <Text color={GREEN}>
                    ({(commit as CommitRef).branch ?? branch?.name})
                  </Text>
                </Box>
                <Text>Date: {commit.date}</Text>
                <Text color={"gray"}>
                  {"   "}
                  {commit.message}
                </Text>
              </Box>
            ))
          ) : (
            <Text color={TEXT}>No commits found</Text>
          )}
        </Box>
      )}
    </>
  );
}
