import { Command } from "commander";
import { InitCommand } from "./commands/init";
import { render } from "ink";
import { AddCommand } from "./commands/add";
import { CommitCommand } from "./commands/commit";
import { CheckoutCommand } from "./commands/checkout";
import { LogCommand } from "./commands/log";
import { BranchCommand } from "./commands/branch";

const program = new Command();

program
  .command("init")
  .description("init a repo")
  .action(() => {
    render(<InitCommand />);
  });

program
  .command("add")
  .argument("[path]")
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

program
  .command("checkout")
  .argument("[commit]")
  .option("-b, --branch <branch>", "specify which branch commit")
  .action((commit, options) => {
    render(<CheckoutCommand commitId={commit} branch={options.branch} />);
  });

program
  .command("log")
  .option("-g, --global", "log all commits")
  .action((options) => {
    render(<LogCommand global={options.global} />);
  });

program
  .command("branch")
  .argument("[name]")
  .option("-d, --delete", "delete a branch")
  .option("-s, --switch", "switch branches")
  .action((name, options) => {
    render(
      <BranchCommand
        name={name}
        isDelete={options.delete}
        isSwitch={options.switch}
      />,
    );
  });

program.parse(process.argv);
