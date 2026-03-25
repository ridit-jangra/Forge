import { Box, Text } from "ink";
import { useEffect, useState } from "react";
import path from "path";
import fs from "fs";
import { matchPaths } from "../utils/forgeIgnore";
import { ACCENT, GREEN, RED, TEXT } from "../colors";
import Spinner from "ink-spinner";
import { addFile } from "../utils/add";

export function AddCommand({ fileOrFolderPath }: { fileOrFolderPath: string }) {
  const [stage, setStage] = useState<"working" | "done">("working");
  const [error, setError] = useState<string | null>(null);
  const [indexAddedCount, setIndexAddedCount] = useState<number>(0);
  const [fileCount, setFileCount] = useState<number>(0);
  const [filesToCheck, setFilesToCheck] = useState<string[]>();
  const [filesChecked, setFilesChecked] = useState<string[]>([]);

  function processFiles(basePath: string, files: (string | Buffer)[]) {
    const normalized = files
      .map((f) => path.join(basePath, f.toString()).replace(/\\/g, "/"))
      .filter((p) => {
        try {
          return fs.statSync(p).isFile();
        } catch {
          return false;
        }
      });

    const checkedFiles = matchPaths(normalized);

    if (checkedFiles.files) {
      setFileCount(checkedFiles.files.length);
      setFilesToCheck(checkedFiles.files);
    } else if (checkedFiles.error) {
      setError(checkedFiles.error);
    }
  }

  useEffect(() => {
    if (fileOrFolderPath === ".") {
      fs.readdir(".", { recursive: true }, (err, files) => {
        if (err) {
          setError(err.message);
          return;
        }
        processFiles(".", files);
      });
    } else {
      fs.stat(fileOrFolderPath, (err, stat) => {
        if (err) {
          setError(err.message);
          return;
        }

        if (stat.isFile()) {
          setFileCount(1);
          setFilesToCheck([fileOrFolderPath]);
        } else {
          fs.readdir(fileOrFolderPath, { recursive: true }, (err, files) => {
            if (err) {
              setError(err.message);
              return;
            }

            processFiles(fileOrFolderPath, files);
          });
        }
      });
    }
  }, []);

  useEffect(() => {
    if (!filesToCheck) return;

    let cancelled = false;

    async function run() {
      let checked: string[] = [];

      if (!filesToCheck) return;

      for (const file of filesToCheck) {
        if (cancelled) return;

        const res = addFile(file, ".");
        if (res.error) {
          setError(res.error);
          return;
        }

        checked.push(file);

        setIndexAddedCount(checked.length);
        setFilesChecked([...checked]);

        await new Promise((r) => setTimeout(r, 10));
      }

      setStage("done");
    }

    run();

    return () => {
      cancelled = true;
    };
  }, [filesToCheck]);

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
        <Box gap={1} flexDirection="column">
          <Box gap={1}>
            <Text color={ACCENT}>
              <Spinner type="dots10" />
            </Text>
            <Text>
              Adding [{indexAddedCount}/{fileCount}]
            </Text>
          </Box>

          <Box flexDirection="column">
            {filesChecked.map((file) => (
              <Box gap={1} key={file}>
                <Text color={GREEN}>✓</Text>
                <Text color={"gray"}>{file}</Text>
              </Box>
            ))}
          </Box>
        </Box>
      )}
      {stage === "done" && (
        <Box flexDirection="column">
          <Text color={GREEN}>✓ Added {indexAddedCount} files</Text>
        </Box>
      )}
    </>
  );
}
