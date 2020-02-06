---
title: "vmdb2: create Debian disk images"
author: Lars Wirzenius
date: work in progress
bindings: vmdb2.yaml
functions: vmdb2.py
...


Introduction
=============================================================================

vmdb2 is a program for producing disk images with Debian installed.
This document is a manual of sorts, and an automated test suite for it.

vmdb2 installs Debian onto a disk, or disk image. It is
like the [debootstrap][] tool, except the end result is a disk or disk
image, not a directory tree. vmdb2 takes care of creating
partitions, and filesystems, and allows some more customization than
vmdebootstrap does.

[vmdb2]: http://vmdb2.liw.fi/
[debootstrap]: https://packages.debian.org/unstable/debootstrap


Specification files
=============================================================================

A vmdb2 specification file is a YAML file that looks like this:

~~~yaml
steps:
  - mkimg: "{{ output }}"
    size: 4G

  - mklabel: gpt
    device: "{{ output }}"

  - mkpart: primary
    device: "{{ output }}"
    start: 0%
    end: 1G
    tag: efi

  - mkpart: primary
    device: "{{ output }}"
    start: 1G
    end: 100%
    tag: /

  - kpartx: "{{ output }}"

  - mkfs: vfat
    partition: efi

  - mkfs: ext4
    partition: /

  - mount: /

  - unpack-rootfs: /

  - debootstrap: buster
    mirror: http://deb.debian.org/debian
    target: /
    unless: rootfs_unpacked

  - apt: install
    packages:
      - linux-image-amd64
    fs-tag: /
    unless: rootfs_unpacked

  - cache-rootfs: /
    unless: rootfs_unpacked

  - fstab: /

  - grub: uefi
    tag: /
    efi: efi
~~~

The list of steps produces the kind of image that the user wants (or
else an unholy mess). The specification file can easily be shared, and
put under version control.

Every action in a step is provided by a plugin to vmdb2. Each action
(technically, "step runner") is a well-defined task, which may be
parameterised by some of the key/value pairs in the step. For example,
`mkimg` would create a disk image file. In the above example it is a
raw disk image file, as opposed to some other format. The image is 4
gigabytes in size. `mkfs` creates an ext4 filesystem in the image
file; in thie example there are no partitions. And so on.

Steps may need to clean up after themselves. For example, a step that
mounts a filesystem will need to unmount it at the end of the image
creation. Also, if a later step fails, then the unmount needs to
happen as well. This is called a "teardown". Some steps are provided
by a plugin that handles the teardown automatically, others may need
to provide instructions for the teardown in the specification file.

By providing well-defined steps that the user may combine as they
wish, vmdb2 gives great flexibility without much complexity, but at
the cost of forcing the user to write a longer specification file than
a simple command line invocation. vmdb2 is based on an earlier
program, vmdebootstrap, that took the other approach, and it proved to
be untenable.


A happy path
=============================================================================

The first case we look at is one for the happy path: a specification
with two echo steps, and nothing else. It's very simple, and nothing
goes wrong when executing it. In addition to the actual thing to do,
each step may also define a "teardown" thing to do. For example, if
the step mounts a filesystem, the teardown would unmount it.

~~~scenario
given a specification file called happy.vmdb
when user runs vmdb2 -v happy.vmdb --output=happy.img
then exit code is 0
then stdout contains "foo" followed by "bar"
then stdout contains "bar" followed by "bar_teardown"
then stdout contains "bar_teardown" followed by "foo_teardown"
~~~

~~~{.file #happy.vmdb .yaml .numberLines}
steps:
- echo: foo
  teardown: foo_teardown
- echo: bar
  teardown: bar_teardown
~~~


Jinja2 templating in specification file values
=============================================================================

vmdb2 allows values in specification files to be processed by the
Jinja2 templating engine. This allows users to do thing such as write
specifications that use configuration values to determine what
happens. For our simple echo/error steps, we will write a rule that
outputs the image file name given by the user. A more realistic
specification file would instead do thing like create the file.

~~~scenario
given a specification file called j2.vmdb
when user runs vmdb2 -v j2.vmdb --output=foo.img 
then exit code is 0
then stdout contains "image is foo.img" followed by "bar"
~~~

~~~{.file #j2.vmdb .yaml .numberLines}
steps:
- echo: "image is {{ output }}"
- echo: bar
~~~


Error handling
=============================================================================

Sometimes things do not quite go as they should. What does vmdb2 do
then?

~~~scenario
given a specification file called unhappy.vmdb
when user runs vmdb2 -v unhappy.vmdb --output=unhappy.img
then exit code is 1
then stdout contains "foo" followed by "yikes"
then stdout contains "yikes" followed by "WAT?!"
then stdout contains "WAT?!" followed by "foo_teardown"
then stdout does NOT contain "bar_step"
then stdout does NOT contain "bar_teardown"
~~~

~~~{.file #unhappy.vmdb .yaml .numberLines}
steps:
- echo: foo
  teardown: foo_teardown
- error: yikes
  teardown: "WAT?!"
- echo: bar
  teardown: bar_teardown
~~~
