import { Command } from "commander";

export const program = new Command()
  .name("rseng-agent-skills")
  .description(
    "Install research software quality skills from RSQKit (EVERSE project) into AI coding agents",
  )
  .version("0.1.0");
