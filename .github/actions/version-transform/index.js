const core = require("@actions/core");
const fs = require('fs')
let version = fs
    .readFileSync(core.getInput("version-path"), "utf8")
    .trim();

version = version.replace(/(-)([0-9]+)/, ".post$2")
version = version.replace(/(.post[0-9]+)(-rc.)/, "$1.dev")
version = version.replace('-rc.', 'rc')

core.setOutput("version", version);
