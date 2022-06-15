const core = require("@actions/core");
const fs = require("fs");
const readline = require("readline");

try {
  const head_version = fs
    .readFileSync(core.getInput("version-path"), "utf8")
    .trim();
  const commits = JSON.parse(core.getInput("commits-json"))
  const changelog = fs.readFileSync(core.getInput("changelog-path"), "utf8");
  let curline = 0;
  const begin = 8;
  let end = Number.MAX_SAFE_INTEGER;
  const rl = readline.createInterface({
    input: fs.createReadStream(core.getInput("changelog-path")),
  });
  let patch = false;
  let minor = false;
  let noupdate = false;
  rl.on("line", (text) => {
    if (curline < begin || curline > end) {
      curline++;
      return;
    }
    if (text.match("\\b" + head_version + "\\b")) {
      end = curline++;
      rl.close();
      return;
    }
    console.log(text);
    if (
      text.includes("### Added") ||
      text.includes("### Changed") ||
      text.includes("### Removed")
    ) {
      minor = true;
      console.log("found minor version update");
    }
    if (text.includes("### Fixed")) {
      patch = true;
      console.log("found patch version update");
    }
    if (
      text.includes("### Tests") ||
      text.includes("### Docs") ||
      text.includes("### Operations")
    ) {
      noupdate = true;
      console.log("found noop header");
    }
    curline++;
  });
  rl.on("close", () => {
    const semver = head_version.split(".");
    let vmajor = semver[0];
    let vminor = semver[1];
    let vpatch = semver[2];
    if (minor) {
      vminor++;
    } else if (patch) {
      vpatch++;
    } else if (noupdate) {
      //do nothing
    } else {
      core.setFailed(
        "Changelog does not contain enough information to update the version."
      );
    }
    const version = vmajor + "." + vminor + "." + vpatch;
    const changelog_header =
      "## [" + version + "] - " + new Date().toISOString().split("T")[0];
    let message = "noop";
    if (minor || patch) {
      message = "The new version will be " + version;
      unreleased = "UNRELEASED";
      let commit_authors = ""
      for (i=0; i < commits.length; i++){
        commit_authors +=  `@${commits[i].author.username} `  
      }

      const new_changelog = changelog
        .slice(0, changelog.indexOf(unreleased) + unreleased.length + 1)
        .concat(
          "\n",
          "\n",
          changelog_header,
          "\n", 
          "### Authors", 
          "\n", 
          `${commit_authors}`,
          "\n",
          changelog.slice(changelog.indexOf(unreleased) + unreleased.length + 1)
        );
      fs.writeFileSync(core.getInput("changelog-path"), new_changelog, "utf8");
      fs.writeFileSync(core.getInput("version-path"), version, "utf8");
    } else if (noupdate) {
      console.log(
        "This PR only contains updates to tests and docs. No release will be created."
      );
    } else {
      console.log("No release will be created due to a failure.");
    }
    core.setOutput("message", message);
  });
} catch (error) {
  core.setFailed(error.message);
}
