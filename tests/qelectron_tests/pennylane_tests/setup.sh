#!/bin/bash

# This script clones the test suite from a specific Pennylane branch/tag

PENNYLANE_VERSION_TAG=$1  # for example, "v0.30.0"
if [[ -z $PENNYLANE_VERSION_TAG ]]; then
	echo "missing Pennylane version tag"
	exit 1
fi

DIR=$(pwd)
CREATE_DIR="${DIR}/pennylane_tests-${PENNYLANE_VERSION_TAG}"


# Clone repo to temp.
git clone --quiet "https://github.com/PennyLaneAI/pennylane" /tmp/pennylane

# Grab specific version.
cd /tmp/pennylane
git checkout --quiet $PENNYLANE_VERSION_TAG

# Copy back to this `pwd`.
echo "creating: ${CREATE_DIR}"
cp -r ./tests/ "${CREATE_DIR}"
cd $DIR

# Clean up.
rm -rf /tmp/pennylane
