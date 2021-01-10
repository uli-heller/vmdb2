#!/bin/sh

set -eu

tarball="$1"
shift

yarn smoke-armhf.yarn --env ROOTFS_TARBALL="$tarball" "$@"
