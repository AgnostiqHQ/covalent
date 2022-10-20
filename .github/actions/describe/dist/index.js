/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 598:
/***/ ((module) => {

module.exports = eval("require")("@actions/core");


/***/ }),

/***/ 792:
/***/ ((module) => {

module.exports = eval("require")("@actions/github");


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/************************************************************************/
/******/ 	/* webpack/runtime/compat */
/******/
/******/ 	if (typeof __nccwpck_require__ !== 'undefined') __nccwpck_require__.ab = __dirname + "/";
/******/
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
const github = __nccwpck_require__(792);
const core = __nccwpck_require__(598);

const run = async () => {
  const token = core.getInput("token");
  const branch = core.getInput("branch");
  let stable = core.getInput("stable");
  if (stable === "true") stable = true;
  else if (stable === "false") stable = false;
  else core.setFailed("There is an error in the stable input");
  const octokit = github.getOctokit(token);
  const {owner:owner,repo:repo} = github.context.repo
  let {
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
        (!tags[i].name.match("rc") || !stable) &&
        tags[i].name.match(re)
      )
        latestTag = tags[i].name;
      i++;
    }
    if (latestTag == null) {
      const { data: data } = await octokit.rest.repos.getCommit({
        owner: owner,
        repo: repo,
        ref: commit,
      });
      if (data.parents.length !== 1) {
        core.setFailed(
          "Branch history is not linear. Try squashing your commits."
        );
        return;
      } else {
        commit = data.parents[0].sha;
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
  .catch(error => {
    core.setFailed(error.message);
  });

})();

module.exports = __webpack_exports__;
/******/ })()
;
