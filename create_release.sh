#!/usr/bin/env bash

# https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/Relativity74205/murkelhausen_app_v2/actions/workflows/129448395/dispatches \
  -d '{"ref":"main"}'

# use to get the workflow id
## https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#list-repository-workflows
#curl -L \
#  -H "Accept: application/vnd.github+json" \
#  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
#  -H "X-GitHub-Api-Version: 2022-11-28" \
#  https://api.github.com/repos/Relativity74205/murkelhausen_app_v2/actions/workflows