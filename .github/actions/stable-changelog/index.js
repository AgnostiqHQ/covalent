const core = require("@actions/core");
const github = require("@actions/github");
const fs = require("fs");
const readline = require("readline");
try {
  const headVersion = fs
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
  let section, lastRelease, isInPrereleaseBlock, isAuthorAlreadyIncluded;
  rl.on("line", (text) => {
    if (text.match("\\b" + headVersion + "\\b")) {
      isInPrereleaseBlock = true;
    } else if (isInPrereleaseBlock && text.match(re)) {
      isInPrereleaseBlock = false;
      lastRelease = text.match(re)[0];
      rl.close();
    } else if (isInPrereleaseBlock && text.includes("### Authors"))
      section = "Authors";
    else if (isInPrereleaseBlock && text.includes("### Added"))
      section = "Added";
    else if (isInPrereleaseBlock && text.includes("### Changed"))
      section = "Changed";
    else if (isInPrereleaseBlock && text.includes("### Removed"))
      section = "Removed";
    else if (isInPrereleaseBlock && text.includes("### Fixed"))
      section = "Fixed";
    else if (isInPrereleaseBlock && text.includes("### Tests"))
      section = "Tests";
    else if (isInPrereleaseBlock && text.includes("### Docs")) section = "Docs";
    else if (isInPrereleaseBlock && text.includes("### Operations"))
      section = "Operations";
    else if (isInPrereleaseBlock && text.includes("##")) section = null;
    else if (isInPrereleaseBlock && text.length > 2 && section === "Authors") {
      isAuthorAlreadyIncluded = summary.Authors.find(author => author.includes(text.split(/[<>]/)[1]))
      if(!isAuthorAlreadyIncluded)
          summary.Authors.push(text);
    } else if (isInPrereleaseBlock && text.length > 2 && section)
      summary[section].push(text);
  });
  rl.on("close", () => {
    const version = headVersion.split("-rc");
    if (version.length < 2)
      core.setFailed("This stable version has already been released.");
    const changelogHeader =
      "## [" + version[0] + "] - " + new Date().toISOString().split("T")[0];
    const unreleased = "UNRELEASED";
    const sections = [];
    Object.keys(summary).forEach((section) => {
      sections.push(`### ${section}`);
      sections.push(summary[section].join("\n"));
    });
    const message = changelogHeader.concat("\n", "\n", sections.join("\n"));

    const new_changelog = changelog
      .slice(0, changelog.indexOf(unreleased) + unreleased.length + 1)
      .concat(message, changelog.slice(changelog.indexOf(lastRelease)));
    fs.writeFileSync(core.getInput("changelog-path"), new_changelog, "utf8");
    fs.writeFileSync(core.getInput("version-path"), version[0], "utf8");
    core.setOutput("message", message);
  }).catch((error) => {
    core.setFailed(error.message);
  });
} catch (error) {
  core.setFailed(error.message);
}
