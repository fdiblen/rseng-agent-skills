#!/bin/sh
# Thin bootstrap only: all real logic lives in the rseng-agent-skills CLI.
set -eu
npx -y rseng-agent-skills install ${AGENTS:-claude}
