#!/bin/bash

set -e

git config --global --add safe.directory '*'

python /semver_tagging.py

NEXT_TAG=$(jq -r .NEXT_TAG semver_result.json)
CHANGELOG=$(jq .CHANGELOG semver_result.json)

echo "next_tag=${NEXT_TAG}" >> "$GITHUB_OUTPUT"
echo "changelog_delta=${CHANGELOG}" >> "$GITHUB_OUTPUT"
