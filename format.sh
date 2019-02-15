#!/bin/sh

set -eu

cleanup()
{
    rm -rf "$tmp"
}

tmp="$(mktemp -d)"
trap cleanup EXIT

version="$(git describe)"
sed "s/^date: .*/date: $version/" vmdb2.mdwn > "$tmp/prelude.mdwn"

pandoc \
    --self-contained \
    --standalone \
    --css vmdb2.css \
    --toc \
    --number-sections \
    -o vmdb2.html \
    "$tmp/prelude.mdwn" vmdb/plugins/*.mdwn

pandoc \
    --toc \
    --number-sections \
    -Vdocumentclass=report \
    -Vgeometry:a4paper \
    -Vfontsize:12pt \
    -Vmainfont:FreeSerif \
    -Vsansfont:FreeSans \
    -Vmonofont:FreeMonoBold \
    '-Vgeometry:top=2cm, bottom=2.5cm, left=2cm, right=1cm' \
    -o vmdb2.pdf \
    "$tmp/prelude.mdwn" vmdb/plugins/*.mdwn
