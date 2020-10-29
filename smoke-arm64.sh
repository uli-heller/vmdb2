#!/bin/sh

set -eu

tarball="$1"
shift

yarn smoke-arm64.yarn --log=stderr --env ROOTFS_TARBALL="$tarball" "$@"
