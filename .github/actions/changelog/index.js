const core = require("@actions/core");
const github = require("@actions/github");
const fs = require("fs");
const semverUtils = require("semver");
const readline = require("readline");

const check_author = (author, authors) => {
  if (
    typeof author === "object" &&
    "email" in author &&
    !authors.includes(author.email)
  ) {
    return "- " + author.name + " <" + author.email + ">\n";
  } else if (
    typeof author === "string" &&
    !authors.includes(author.split(/[<>]/)[1])
  ) {
    return "- " + author + "\n";
  } else {
    return "";
  }
};

const get_author = (commit, authors) => {
  let output = "";
  if (commit.author && commit.author.type === "User") {
    output += check_author(commit.commit.author, authors);
    const coauthors = commit.commit.message.match(/Co-authored-by:.+<.+@.+>/g);
    for (author in coauthors) {
      output += check_author(coauthors[author], authors + output);
    }
  }
  return output;
};

try {
  const token = core.getInput("token");
  const head_version = fs
    .readFileSync(core.getInput("version-path"), "utf8")
    .trim();
  const changelog = fs.readFileSync(core.getInput("changelog-path"), "utf8");
  const basehead = core.getInput("basehead");
  const {owner:owner,repo:repo} = github.context.repo
  const octokit = github.getOctokit(token);
  octokit.rest.repos
    .compareCommitsWithBasehead({
      owner: owner,
      repo: repo,
      basehead: basehead,
    })
    .then((compareCommits) => {
      const {
        data: { commits: commits },
      } = compareCommits;
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

        let semver = semverUtils.valid(head_version);

        if(!semver){
          core.setFailed(
            `Invalid Semver for VERSION file contents: ${head_version}`
          );
        } else if (!minor && !noupdate && !patch) {
          core.setFailed(
            "Changelog does not contain enough information to update the version."
          );
        }
        let simplifiedSemver = `${semverUtils.major(semver)}.${semverUtils.minor(semver)}.${semverUtils.patch(semver)}`;

        console.log(`VERSION file contents: ${head_version} | Parsed: ${semver} | Simplified: ${simplifiedSemver}`)

        if(minor){
          simplifiedSemver = semverUtils.inc(simplifiedSemver,'minor')
        }
        else if(patch){
          simplifiedSemver = semverUtils.inc(simplifiedSemver,'patch')
        }

        const version = `${simplifiedSemver}-rc.0`;

        console.log(`Incremented semver version: ${simplifiedSemver}`);

        const changelog_header =
          "## [" + version + "] - " + new Date().toISOString().split("T")[0];

        let message = "noop";

        if (minor || patch) {
          message = "The new version will be " + version;
          unreleased = "UNRELEASED";
          let commit_authors = "";
          for (i = 0; i < commits.length; i++) {
            commit_authors += get_author(commits[i], commit_authors);
          }

          const new_changelog = changelog
            .slice(0, changelog.indexOf(unreleased) + unreleased.length + 1)
            .concat(
              "\n",
              "\n",
              changelog_header,
              "\n",
              "\n",
              "### Authors",
              "\n",
              "\n",
              `${commit_authors}`,
              changelog.slice(
                changelog.indexOf(unreleased) + unreleased.length + 1
              )
            );
          fs.writeFileSync(
            core.getInput("changelog-path"),
            new_changelog,
            "utf8"
          );
          fs.writeFileSync(core.getInput("version-path"), version, "utf8");
        } else if (noupdate) {
          console.log(
            "This PR only contains updates to tests and docs. No release will be created."
          );
        } else {
          console.log("No release will be created due to a failure.");
        }
        console.log(message)
        core.setOutput("message", message);
        core.setOutput("version", version)
      });
    })
    .catch((error) => {
      core.setFailed(error.message);
    });
} catch (error) {
  core.setFailed(error.message);
}
