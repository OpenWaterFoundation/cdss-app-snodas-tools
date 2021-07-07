# Ubuntu OS Upgrade #

The following is the documentation of upgrading the Ubuntu OS from 16.04 to 20.04.
an attempt will first be made to upgrade from 16.04 to 18.04, then 18.04 to 20.04.
It contains some troubleshooting, since the initial OS version has officially reached
its EoL and is no longer supported. In normal circumstances, using 3 commands in a
terminal would be all that's needed to perform the update. An unsupported OS version
however might have uncommon issues and errors.

## Steps ##

1. Open a command line terminal. Type `do-release-upgrade -c` to check what version
of Ubuntu the upgrade will try to install to confirm it's either the desired version,
or the next version needed.
2. Type `sudo apt update`.
3. Type `sudo apt upgrade`.
    * See [Linux Headers Reinstall](#linux-headers-reinstall) for troubleshooting.
4. Type `sudo do-release-upgrade`.
5. Repeat steps 2-4 for each version increase, like the discussed 16.04 -> 18.04 and
18.04 -> 20.04 mentioned above.

## Troubleshooting ##

The following are roadblocks and other issues that occurred when attempting the
upgrade, and their work arounds.

### Linux Headers Reinstall ###

`E: The package linux-headers-... needs to be reinstalled, but I can't find an archive for it.`

The Ubuntu version attempting the upgrade is obsolete, and it and its headers are
not in the repository anymore. It needs to be reinstalled so it can be upgraded
to the next version.

It seemed like the /etc/apt/sources.list file was incorrect from the start. Since
the original version used was 16.04, Xenial should have been where packages were
retrieved from, but bionic was in the file instead. Replacing all instances of bionic
with xenial, then running `sudo apt update` and `sudo apt upgrade` fixed

### Miscellaneous Notes ###

The package `google-compute-engine` needed to be removed in order to perform the
`sudo apt upgrade` on the 16.04 version. It wasn't known if that would break
anything after the update to 20.04, but there doesn't seem to be. There is another
installed package called `google-compute-engine-oslogin` which seems to be the newer
renamed package for the Google Compute Engine.

One of the errors the `sudo apt update` command claimed a package was not installed
that needed to be. It's name was slightly different then the linux-headers package;
instead of ending in gcp, gcp was towards the beginning of the package name.
Installing said package seemed to help along the update process as well.