const core = require("@actions/core");
const github = require("@actions/github");
const fs = require("fs");
const readline = require("readline");
try {
  const head_version = fs
    .readFileSync(core.getInput("version-path"), "utf8")
    .trim();
  const changelog = fs.readFileSync(core.getInput("changelog-path"), "utf8");
  const rl = readline.createInterface({
    input: fs.createReadStream(core.getInput("changelog-path")),
  });
  const re = /\[\d+\.\d+\.\d+(-\d+)*?\]/;
  const summary = {
    Authors: [],
    Added: [],
    Changed: [],
    Removed: [],
    Fixed: [],
    Tests: [],
    Docs: [],
    Operations: [],
  };
  let curline = 0;
  let begin = Number.MAX_SAFE_INTEGER;
  let end = Number.MAX_SAFE_INTEGER;
  let section, i, last_release;
  rl.on("line", (text) => {
    if (text.match("\\b" + head_version + "\\b")) {
      begin = curline++;
      return;
    }
    if (curline < begin || curline > end) {
      curline++;
      return;
    }
    if (text.match(re)) {
      end = curline++;
      last_release = text.match(re)[0];
      rl.close();
      return;
    }
    console.log(text);
    if (text.includes("### Authors")) section = "Authors";
    else if (text.includes("### Added")) section = "Added";
    else if (text.includes("### Changed")) section = "Changed";
    else if (text.includes("### Removed")) section = "Removed";
    else if (text.includes("### Fixed")) section = "Fixed";
    else if (text.includes("### Tests")) section = "Tests";
    else if (text.includes("### Docs")) section = "Docs";
    else if (text.includes("### Operations")) section = "Operations";
    else if (text.includes("##")) section = null;
    else if (text.length > 2 && section === "Authors") {
      i = 0;
      while (text && i < summary.Authors.length) {
        if (summary.Authors[i].includes(text.split(/[<>]/)[1])) text = null;
        i++;
      }
      if (text) summary.Authors.push(text);
    } else if (text.length > 2 && section) summary[section].push(text);
    curline++;
  });
  rl.on("close", () => {
    const version = head_version.split("-rc");
    if (version.length < 2)
      core.setFailed("This stable version has already been released.");
    const changelog_header =
      "## [" + version[0] + "] - " + new Date().toISOString().split("T")[0];
    const unreleased = "UNRELEASED";
    const sections = [];
    Object.keys(summary).forEach((section) => {
      sections.push(`### ${section}`);
      sections.push(summary[section].join("\n"));
    });
    const message = changelog_header.concat("\n", "\n", sections.join("\n"));

    const new_changelog = changelog
      .slice(0, changelog.indexOf(unreleased) + unreleased.length + 1)
      .concat(message, changelog.slice(changelog.indexOf(last_release)));
    fs.writeFileSync(core.getInput("changelog-path"), new_changelog, "utf8");
    fs.writeFileSync(core.getInput("version-path"), version[0], "utf8");
    core.setOutput("message", message);
  }).catch((error) => {
    core.setFailed(error.message);
  });
} catch (error) {
  core.setFailed(error.message);
}
