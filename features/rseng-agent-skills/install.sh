#!/bin/sh
# Thin bootstrap only: all real logic lives in the rseng-agent-skills CLI.
# The version is pinned rather than floating: this runs unattended during
# a container build, so an unpinned `npx -y` would fetch and execute
# whatever the registry serves at build time.
set -eu
npx -y rseng-agent-skills@0.1.0 install ${AGENTS:-claude} --yes
