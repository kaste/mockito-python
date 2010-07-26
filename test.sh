#!/usr/bin/env bash

# Run unit tests against multiple versions of python.

VERSIONS=( 2.4 2.5 2.6 2.7 3 )

for version in ${VERSIONS[@]}; do
    python${version} setup.py test -q
    echo "Test results for version ${version}. Press <enter> to continue."
    read
done

