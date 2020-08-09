#!/bin/sh

set -eu

cleanup()
{
    rm -f tmp.md
}

trap cleanup EXIT

(cat vmdb2.md; for x in vmdb/plugins/*.mdwn; do cat "$x"; echo; done) > tmp.md
if command -v sp-docgen > /dev/null
then
    sp-docgen tmp.md -o vmdb2.html
    if command -v pdflatex > /dev/null
    then
	sp-docgen tmp.md -o vmdb2.pdf
    fi
else
    pandoc \
	--self-contained \
	--standalone \
	--css vmdb2.css \
	--toc \
	--number-sections \
	-o vmdb2.html \
	tmp.md

    if command -v pdflatex > /dev/null
    then
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
            tmp.md
    fi
fi
