#!/bin/sh

set -eu

tarball="$1"
shift

yarn smoke-ppc64el.yarn --env ROOTFS_TARBALL="$tarball" "$@"
