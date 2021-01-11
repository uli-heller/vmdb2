#!/bin/sh

set -eu

tarball="$1"
shift

yarn smoke-amd64.yarn --env ROOTFS_TARBALL="$tarball" "$@"
