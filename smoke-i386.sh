#!/bin/sh

set -eu

tarball="$1"
shift

yarn smoke-i386.yarn --env ROOTFS_TARBALL="$tarball" "$@"
