[vmdb2]: http://vmdb2.liw.fi/
[debootstrap]: https://packages.debian.org/unstable/debootstrap
[HTML]: https://vmdb2-manual.liw.fi/
[PDF]: https://vmdb2-manual.liw.fi/vmdb2.pdf


# Introduction

[vmdb2][] builds disk images with Debian installed. The images can be
used for virtual machines, or can be written to USB flash memory
devices, and hardware computers can be booted off them.

This manual is published as [HTML][] and as [PDF][].


## Installation

You can get vmdb2 by getting the source code from git, either
[author's server][] or [gitlab.com][].

[author's server]: http://git.liw.fi/vmdb2/
[gitlab.com]: https://gitlab.com/larswirzenius/vmdb2

You can then run it from the source tree:

~~~sh
$ sudo /path/to/vmdb2/vmdb2 ...
~~~

In Debian 10 ("buster") and its derivatives, you can also install the
vmdb2 package:

~~~sh
$ apt install vmdb2
~~~

For any other systems, we have no instructions. If you figure it out,
please tell us how.


## Why vmdb2 given vmdebootstrap already existed

vmdb2 is a successor of the vmdebootstrap program, written by the same
author, to fix a number of architectural problems and limitations with
the old program. The new program is not compatible with the old one;
that would've required keeping the problems, as well.

`vmdebootstrap` was the first attempt by it author to write a tool to
build system images. It turned out to not be well designed.
Specifically, it was not easily extensible to be as flexible as a tool
of this sort should be.


## Why vmdb2 given other tools already exist

The author likes to write tools for himself and had some free time. He
sometimes prefers to write his own tools rather than spend time and
energy evaluating and improving existing tools. He admits this is a
character flaw.

Also, he felt ashamed of how messy `vmdebootstrap` turned out to be.

If nobody else likes `vmdb2`, that just means the author had some fun
on his own.


# Getting started

You need to make a *specification file* (in YAML) that tells vmdb2
what kind of image to build, and how. An example:

~~~{.yaml .numberLines}
steps:
  - mkimg: "{{ output }}"
    size: 4G
  - mklabel: msdos
    device: "{{ output }}"
  - mkpart: primary
    device: "{{ output }}"
    start: 0%
    end: 100%
    tag: /
  - kpartx: "{{ output }}"
  - mkfs: ext4
    partition: /
  - mount: /
  - debootstrap: buster
    mirror: http://deb.debian.org/debian
    target: /
  - apt: install
    packages:
    - linux-image-amd64
    tag: /
  - fstab: /
  - grub: bios
    tag: /
~~~

The source repository of vmdb2 has more examples, which are also
automatically tested, unlike the above one.

The list of steps builds the kind of image that the user wants. The
specification file can easily be shared, and put under version
control.

Every action in a step is provided by a plugin to vmdb2. Each action
is a well-defined task, which may be parameterised by some of the
key/value pairs in the step. For example, `mkimg` would create a raw
disk image file. The image is 4 gigabytes in size. `mkpart` creates a
partition, and `mkfs` an ext4 filesystem in the partition. And so on.

Steps may need to clean up after themselves. For example, a step that
mounts a filesystem will need to unmount it at the end of the image
creation. Also, if a later step fails, then the unmount needs to
happen as well. This is called a "teardown".

By providing well-defined steps that the user may combine as they
wish, vmdb2 gives great flexibility without much complexity, but at
the cost of forcing the user to write a longer specification file than
a simple command line invocation.

To use this, save the specification into `test.vmdb`, and run the
following command:

~~~sh
$ sudo vmdb2 test.vmdb --output test.img --verbose
~~~

Alternatively the specification can be passed in via stdin by setting the
file name to `-`, like so:

~~~sh
$ cat test.vmdb | sudo vmdb2 - --output test.img --verbose
~~~

This will take a long time, mostly at the `debootstrap` step. See
below for speeding that up by caching the result.

Due to the kinds of things vmdb2 does (such as mounting, creating
device nodes, etc), it needs to be run using root privileges. For the
same reason, it probably can't be run in an unprivileged container.


## All images must be partitioned

At this time, vmdb2 does not support building partitioned images
without partition, or images without a partition table. Such support
may be added later. If this would be useful, do tell the authors.


## Tags

Instead of device filenames, which vary from run to run, vmdb2 steps
refer to block devices inside the image, and their mount points, by
symbolic names called tags. Tags are any names that the user likes,
and vmdb2 does not assign meaning to them. They're just strings.


## Jinja2 expansion

To refer to the filename specified with the `--output` or `--image`
command line options, you can use [Jinja2](http://jinja.pocoo.org/)
templating. The variables `output` and `image` can be used.

~~~yaml
- mkimg: "{{ output }}"
- mklabel: "{{ image }}"
~~~

The difference is that `--output` creates a new file, or truncates an
existing file, whereas `--images` requires the file to already exist.
The former is better for image file, the latter for real block
devices.


## Speed up image creation by caching

Building an image can take several minutes, and that's with fast
access to a Debian mirror and an SSD. The slowest part is typically
running debootstrap, and that always results in the same output, for a
given Debian release. This means its easy to cache.

vmdb2 has the two actions `cache-roots` and `unpack-rootfs` and the
command line option `--rootfs-tarball` to allow user to cache. The
user uses the option to name a file. `cache-rootfs` takes the root
filesystem and stores it into the file as a compress tar archive
("tarball"). `unpack-rootfs` unpacks the tarball. This allows vmdb2 to
skip running debootstrap needlessly.

The specify which steps should be skipped, the `unless` field can be
used: `unpack-rootfs` sets the `rootfs_unpacked` flag if it actually
unpacks a tarball, and `unless` allows checking for that flag. If the
tarball doesn't exist, the flag is not set.

~~~yaml
- unpack-rootfs: root

- debootstrap: buster
  target: root
  unless: rootfs_unpacked

- cache-rootfs: root
  unless: rootfs_unpacked
~~~

If the tarball exists, it is unpacked, and the `debootstrap` and
`cache-rootfs` steps are skipped. If the tarball doesn't exist, the
unpack step is silently skipped, and the debootstrap and caching steps
are performed instead.

It's possible to have any number of steps between the unpack and the
cache steps. However, note that if you change anything within those
steps, or time passes and you want to include the new packages that
have made it into Debian, you need to delete the tarball so it is run
again.


# Acceptance criteria

[Subplot]: https://subplot.liw.fi/

This chapter documents the user-level acceptance criteria for vmdb2,
and how they are to be verified. It's meant to be processed with the
[Subplot][] tool, but understood by all users of and contributors to
the vmdb2 software. The criteria and their verification are expressed
as *scenarios*.

For reasons of speed, security, and reliability, these scenarios test
only the core functionality of vmdb2. All the useful steps for
actually building images are left out.. Those are tested by actually
building images. However, those useful steps are not useful, if the
core that invokes them is rotten.


## A happy path

The first case we look at is one for the happy path: a specification
with two echo steps, and nothing else. It's very simple, and nothing
goes wrong when executing it. In addition to the actual thing to do,
each step also defines a "teardown" thing to do. We check that all the
steps and teardown steps are performed, in the right order.

Note that the "echo" step is provided by vmdb2 explicitly for this
kind of testing, and that the teardown field in the step is
implemented by the echo step. It's not a generic feature.

~~~scenario
given a specification file called happy.vmdb
when user runs vmdb2 -v happy.vmdb --output=happy.img
then exit code is 0
and stdout contains "foo" followed by "bar"
and stdout contains "bar" followed by "bar_teardown"
and stdout contains "bar_teardown" followed by "foo_teardown"
~~~

~~~{.file #happy.vmdb .yaml .numberLines}
steps:
- echo: foo
  teardown: foo_teardown
- echo: bar
  teardown: bar_teardown
~~~


## Jinja2 templating in specification file values

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
and stdout contains "image is foo.img" followed by "bar"
~~~

~~~{.file #j2.vmdb .yaml .numberLines}
steps:
- echo: "image is {{ output }}"
- echo: bar
~~~


## Error handling

Sometimes things do not quite go as they should. Does vmdb2 do things
in the right order then? This scenario uses the "error" step provided
for testing this kind of thing.

~~~scenario
given a specification file called unhappy.vmdb
when user runs vmdb2 -v unhappy.vmdb --output=unhappy.img
then exit code is 1
and stdout contains "foo" followed by "yikes"
and stdout contains "yikes" followed by "WAT?!"
and stdout contains "WAT?!" followed by "foo_teardown"
and stdout does NOT contain "bar_step"
and stdout does NOT contain "bar_teardown"
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


# Step reference manual


---
title: Building Debian system images with vmdb2
author: Lars Wirzenius
bindings: vmdb2.yaml
functions: vmdb2.py
documentclass: report
...

