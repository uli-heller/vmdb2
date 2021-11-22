README for vmdb2 or vmdebootstrap 2nd generation     ; -*- mode: markdown;-*-
=============================================================================


**Note:** vmdb2 is in "selfish maintenance mode". Lars maintains the
software to the extent he needs it, but is not spending time to
develop new features or debug problems he doesn't see himself. He will
review patches, however, so if you want vmdb2 to improve, make a
change and submit it for review.


[vmdb2][] is a program for producing a disk image with Debian
installed.

[vmdb2]: https://vmdb2.liw.fi/

Introduction
-----------------------------------------------------------------------------

[vmdebootstrap][] installs Debian onto a disk image. It is like the
[debootstrap][] tool, except the end result is a bootable disk image,
not a directory. vmdebootstrap takes care of creating partitions, and
filesystems, and allows some more customization than the older
vmdebootstrap does.

vmdebootstrap is also a messy pile of kludge, and rather inflexible.
vmdb2 is a re-implementation from scratch, without a need for
backwards compatibility. It aims to provide more flexibility than
vmdebootstrap, without becoming anywhere near as complicated. Think of
vmdb2 as "vmdebootstrap the second generation". The name has changed
to allow the two tools to installable in parallel, which is important
for a transition period.

The main user-visible difference between vmdebootstrap and vmdb2 is
that the older program provides extensibility via a legion of command
line options and the newer program by providing a domain specific
language to express what kind of Debian system is to be created.

(Lars Wirzenius wrote both vmdebootstrap and vmdb2 and is entitled to
sneer at his younger self. It's his way of dealing with the mountain
of guilt of making something as awful as vmdebootstrap.)

[vmdebootstrap]: http://liw.fi/vmdebootstrap/
[debootstrap]: https://packages.debian.org/unstable/debootstrap


Getting vmdb2
-----------------------------------------------------------------------------

vmdb2 source code is available via git:

* <http://git.liw.fi/vmdb2>
* <https://gitlab.com/larswirzenius/vmdb2>

It used to be on GitHub as well, but was withdrawn from there due to
GitHub being a proprietary service.

Requirements:

The following tools are used by vmdb2 (Debian package names in brackets).

* `kpartx` [kpartx, mkpart command]
* `parted` [`parted`, mklabel command]
* `qemu-img` [`qemu-utils`, mkimg command]
* `qemu-user-static` [`qemu-user-static`, qemu-debootstrap command]
* `zerofree` [`zerofree`, zerofree command]

The following Python modules are used by vmdb2 (Debian package names in brackets).

* jinja2 [`python3-jinja2`]
* yaml [`python3-yaml`]

If UEFI booting is to be used, firmware is needed for the following
architectures (Debian package names providing it in brackets):

* amd64 [`ovmf`]
* arm64 [`qemu-efi-aarch64`]
* arm [`qemu-efi-arm`]
* i386 [`ovmf-ia32`]


Dependencies for smoke.sh
-----------------------------------------------------------------------------

You probably need the following installed to run the smoke tests:

- git
- python3-coverage-test-runner
- python3-jinja2
- cmdtest 0.31 or later
- qemu-utils
- parted
- kpartx
- debootstrap
- expect
- qemu-system
- ovmf
- ovmf-ia32
- qemu-efi-aarch64
- qemu-efi-arm
- zerofree


Tutorial
-----------------------------------------------------------------------------

To use vmdb2, git clone the source and at the root of the source tree
run the following command:

    sudo ./vmdb2 --output pc.img pc.vmdb --log pc.log

`--output pc.img` specifies that the output image is called
`pc.img`, the specification is `pc.vmdb` and the log file goes
to `pc.log`.


Plugins and steps
-----------------------------------------------------------------------------

The `vmdb2` architecture consists of a main program that reads the
input file, finds a matching "step runner" for each step used in the
input file, and then runs the steps in order. If there's a problem, it
runs corresponding "teardown" steps in reverse order of the steps.

A step might be "mount this filesystem", and the corresponding
teardown is "unmount".

Steps (and teardowns) are provided by plugins; see the `vmdb/plugins`
directory in the source tree. Steps are intended to be very cohesive
and lowly coupled. They may share some state (such as mounted
filesystems) via the `State` object, but not in any other way. A
plugin may only provide one step runner.

See `pc.vmdb` and other `.vmdb` files for examples. Note how the file
uses Jinja2 templating for value fields to get value of `--output` in
the right places. Also note how creating a partition or mounting a
filesystem assigns a "tag" that can be referenced in steps where the
partition/filesystem is needed, without having to know the actual path
to the device node or mount point.


Writing plugins
-----------------------------------------------------------------------------

More step runners would be good, but will be added based on
actual reported needs by users ("I need to have this to..."), not
speculatively ("This seems like a good idea").

To write a plugin, see the existing ones for examples, and put it in
`vmdb/plugins/foo_plugin.py` for some value of `foo`. The plugin file
should provide a class named `FooPlugin`, which should provide the
interface defined by `vmdb.Plugin`. Most plugins add a step runner,
which subclasses `vmdb.StepRunnerInterface`, and the plugin class adds
the step runner to the application's global list of step runners. See
existing plugins for examples.

Note that each plugin may only add one step runner. This keeps things
simple, and also keeps document formatting simple. If two plugins
need to share code for some reason, it may be appropriate to put that
code into the `vmdb` module.

You should document the plugin in a Markdown file next to it:
`vmdb/plugins/foo.mdwn` for plugin mentioned above. See existing
documentation files for a model. You should mention all keys each step
can use, and give an example. It would be great to explain when the
plugin would be useful. Try to keep source lines to less than 80
characters.

Plugins are meant to be very easy to write. If not, there's probably
something wrong with `vmdb2`. Please raise the issue.


Hacking
-----------------------------------------------------------------------------

To run automated tests:

    ./check

This only runs the unit tests and build tests. To run a smoke test
that actually builds and boots images:

    sudo ./smoke.sh cache.tar.gz

where `cache.tar.gz` caches the debootstrap output for a future run.

You'll need the yarn program (part of the [cmdtest][] package), and
also [CoverageTestRunner][] for running the unit tests.

[cmdtest]: http://liw.fi/cmdtest/
[CoverageTestRunner]: http://liw.fi/coverage-test-runner/

Try to follow PEP8 for code formatting, and try to keep lines shorter
than 80 characters.

Make sure ./check and check-all scripts pass both before and after
your modifications.


Contact
-----------------------------------------------------------------------------

To contact Lars, email is best: `liw@liw.fi`.

There is an IRC channel for vmdb2: irc.oftc.net network, `#vmdb2`.


Legalese
-----------------------------------------------------------------------------

Copyright 2017-2019  Lars Wirzenius

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

=*= License: GPL-3+ =*=
