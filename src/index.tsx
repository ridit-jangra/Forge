import { Command } from "commander";
import { InitCommand } from "./commands/init";
import { render } from "ink";

const program = new Command();

program
  .command("init")
  .description("init a repo")
  .action(() => {
    render(<InitCommand />);
  });

program.parse(process.argv);
