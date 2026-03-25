import { Command } from "commander";
import { InitCommand } from "./commands/init";
import { render } from "ink";
import { AddCommand } from "./commands/add";
import { CommitCommand } from "./commands/commit";

const program = new Command();

program
  .command("init")
  .description("init a repo")
  .action(() => {
    render(<InitCommand />);
  });

program
  .command("add <path>")
  .description("add a file or everything")
  .action((path) => {
    render(<AddCommand fileOrFolderPath={path} />);
  });

program
  .command("commit")
  .argument("[path]")
  .requiredOption("-m, --message <msg>", "commit message")
  .option("-a, --all", "commit all files")
  .action((path, options) => {
    render(
      <CommitCommand
        message={options.message}
        isAll={options.all}
        singlePath={path}
      />,
    );
  });

program.parse(process.argv);
