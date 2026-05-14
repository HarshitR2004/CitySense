#!/usr/bin/env node

const { spawnSync } = require("child_process");

const args = process.argv.slice(2);
const platform = args[0];
const extraArgs = args.slice(1);

const expoArgs = ["start"];

if (platform === "web") {
  expoArgs.push("--web");
} else if (platform === "android") {
  expoArgs.push("--android");
} else if (platform === "ios") {
  expoArgs.push("--ios");
} else if (platform && !platform.startsWith("-")) {
  expoArgs.push(platform);
}

expoArgs.push(...extraArgs);

if (process.env.CITYSENSE_START_NO_RUN === "1") {
  console.log(`expo ${expoArgs.join(" ")}`);
  process.exit(0);
}

const result = spawnSync("npx", ["expo", ...expoArgs], {
  stdio: "inherit",
  shell: true,
});

process.exit(result.status ?? 1);