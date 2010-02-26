#!/usr/bin/env bash

# Run unit tests against multiple versions of python.

cd mockito_test

VERSIONS=( 2.4 2.5 2.6 )

for version in ${VERSIONS[@]}; do
    python${version} all_tests.py
    echo "Test results for version ${version}. Press <enter> to continue."
    read
done

cd ..

