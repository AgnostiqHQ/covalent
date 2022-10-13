const github = require("@actions/github");
const core = require("@actions/core");

const run = async () => {
  const token = core.getInput("token");
  const branch = core.getInput("branch");
  let stable = core.getInput("stable");
  if (stable === "true") stable = true;
  else if (stable === "false") stable = false;
  else core.setFailed("There is an error in the stable input");
  const octokit = github.getOctokit(token);
  const {owner:owner,repo:repo} = github.context.repo
  const {
    data: {
      object: { sha: commit },
    },
  } = await octokit.rest.git.getRef({
    owner: owner,
    repo: repo,
    ref: `heads/${branch.replace("refs/heads/", "")}`,
  });
  const { data: tags } = await octokit.rest.repos.listTags({
    owner: owner,
    repo: repo,
  });
  const re = /\d+\.\d+\.\d+(-\d+)*?/;
  let latestTag, i;
  while (latestTag == null) {
    i = 0;
    while (i < tags.length && latestTag == null) {
      if (
        commit === tags[i].commit.sha &&
        (!tag.name.match("rc") || !stable) &&
        tag.name.match(re)
      )
        latestTag = tag.name;
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
        core.setFailed(
          "Branch history is not linear. Try squashing your commits."
        );
        return;
      } else {
        commit = parents[0].sha;
      }
    }
  }
  if (latestTag == null) {
    core.setFailed(
      "The action couldn't find a matching recent tag. Did you create your branch from a release tag?"
    );
    return;
  } else {
    core.setOutput("tag", latestTag);
  }
};

run()
  .catch(error => error)
  .then((error) => {
    core.setFailed(error?.message);
  });
