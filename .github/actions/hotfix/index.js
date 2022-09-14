const github = require("@actions/github");
const core = require("@actions/core");

const failure = (message) => {
  core.setOutput("comment", message);
  core.setFailed(message);
};

const run = async () => {
  const token = core.getInput("token");
  const octokit = github.getOctokit(token);
  const owner = github.context.payload.repository.organization;
  const repo = github.context.payload.repository.name;
  const { data: pr } = await octokit.rest.pulls.get({
    owner: owner,
    repo: repo,
    pull_number: github.context.pullRequest.number,
  });
  const { data: tags } = await octokit.rest.repos.listTags({
    owner: owner,
    repo: repo,
  });
  const squashFailure = "Please squash your commits before applying a hotfix.";
  let commit = pr.head.sha;
  let commits = 0;
  let latestTag, i, version;
  while (commits < 2 && latestTag == null) {
    i = 0;
    while (i < tags.length && latestTag == null) {
      if (commit === tags[i].commit.sha) latestTag = tag.name;
      i++;
    }
    if (latestTag == null) {
      const { data: data } = await octokit.rest.repos.getCommit({
        owner: owner,
        repo: repo,
        ref: commit,
      });
      const parents = data.commit.parents;
      if (parents.length !== 1) {
        failure(squashFailure);
        return
      }
      else {
        commit = parents[0].sha;
        commits++;
      }
    }
  }
  if (latestTag == null) {
    failure(
      "The action couldn't find a matching recent tag. Did you create your branch from a release tag?"
    );
    return
  }
  else {
    const { data: release } = octokit.rest.repos.getReleaseByTag({
      owner: owner,
      repo: repo,
      tag: latestTag,
    });
    const hotfixVersion = latestTag.split("-");
    if (!release.prerelease && hotfixVersion.length > 1)
      version = `${latestTag}-${Number(hotfixVersion[1]) + 1}`;
    else if (!release.prerelease) version = `${latestTag}-1`;
    else {
      failure("Hotfix branches must be created from a stable release.");
      return
    }
    core.setOutput(
      "message",
      `${github.context.payload.event.issue.title} (#${github.context.payload.event.issue.number})`
    );
    core.setOutput(
      "comment",
      `Hotfix ${version} has been created. You may contact mall security to create a stable release using this tag.`
    );
    core.setOutput("version", version);
  }
};

run()
  .catch(error)
  .then((error) => {
    core.setFailed(error.message);
  });
