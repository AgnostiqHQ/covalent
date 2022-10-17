const core = require("@actions/core");
const fs = require('fs')
let version = fs
    .readFileSync(core.getInput("version-path"), "utf8")
    .trim();

console.log("Intended version transformations (Semver -> PEP440):")
console.log("A.B.C -> A.B.C (stable release)")
console.log("A.B.C-D -> A.B.C.postD (post-release)")
console.log("A.B.C-rc.D -> A.B.CrcD (release candidate / pre-release)")
console.log("A.B.C-D-rc.E -> A.B.C.postD.devE (development pre-release between release and post-release)")

console.log(`\nOriginal VERSION file: ${version}`)
version = version.replace(/(-)([0-9]+)/, ".post$2")
version = version.replace(/(.post[0-9]+)(-rc.)/, "$1.dev")
version = version.replace('-rc.', 'rc')

console.log(`New VERSION output: ${version}`)
core.setOutput("version", version);
