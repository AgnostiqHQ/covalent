#!/bin/bash

# This script clones the test suite from a specific Pennylane branch/tag

PENNYLANE_VERSION_TAG=$1  # for example, "v0.30.0"

if [[ -z $PENNYLANE_VERSION_TAG ]]; then
	echo "missing Pennylane version tag"
	exit 1
fi

DIR=$(pwd)
QE_TESTS_DIR=$(dirname $DIR)

git clone --quiet "https://github.com/PennyLaneAI/pennylane" /tmp/pennylane

cd /tmp/pennylane
git checkout --quiet $PENNYLANE_VERSION_TAG
cp -r ./tests/ "${QE_TESTS_DIR}/pennylane_tests-${PENNYLANE_VERSION_TAG}/"
cd $DIR

rm -rf /tmp/pennylane
