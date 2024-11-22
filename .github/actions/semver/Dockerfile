# Container image that runs your code
FROM python:3.11.5-slim

RUN apt-get update && apt-get install -y git jq

RUN pip install --upgrade pip && pip install PyGithub==2.1.1

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.sh /entrypoint.sh
COPY semver_tagging.py /semver_tagging.py

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
