# AmogOS 2.x Builder

Build a complete **AmogOS 2 Pro 2.1 Debian x86_64 live ISO** from an empty
Debian bootstrap and the configuration in this repository. There is no dependency
on a private server, pre-existing root filesystem or earlier ISO.

- `amogos-debian/`: Debian package lists, source lock, container, boot menu and edition overlay.
- `amogos-arch/`: intentionally empty, reserved for the future Arch edition.
- `shared/`: numbered wallpapers, desktop profile, menu icon and Fastfetch configuration.
- `builder/`: separate modules for bootstrap, packages, drivers, configuration, mounting and ISO assembly.
- `tests/`: filesystem-boundary and input validation checks.

## Build on Debian 13

Use an x86_64 Linux machine, at least 4 GiB RAM and 20 GiB free space. An internet
connection is required. Bootstrap and ISO tools require root and mount namespaces.

```bash
git clone https://github.com/amogosbuild/AmogOS-2.x-Builder.git
cd AmogOS-2.x-Builder
./build.sh --check
sudo ./build.sh amogos-debian --install-dependencies
```

The optional dependency flag installs the Debian build tools on the build host.
Subsequent builds may omit it. Work trees are unique and retained under `.work/`
for inspection. Completed ISOs, SHA-256 files, package inventories and build
manifests are written to `out/`. Existing output files are never overwritten.

```bash
sudo ./build.sh amogos-debian --work-dir /path/to/build-work --output-dir /path/to/isos
```

## Build in a container

On another x86_64 Linux distribution, install Docker or Podman first:

```bash
./build.sh amogos-debian --container
./build.sh amogos-debian --container --engine podman
```

The selected engine must permit privileged containers and mount namespaces.
The container receives the source checkout read-only and only the selected work
and output folders as writable mounts. Its Debian userspace is defined by
`amogos-debian/Containerfile`. Windows users need a suitable Linux VM or WSL2
environment; this is not a native Windows ISO build.

## What the Debian image includes

The scripts install Plasma, the AmogOS desktop profile, numbered wallpapers,
Amogus menu icon, Fastfetch aliases, Steam, broad Wi-Fi firmware and Mesa graphics.
NVIDIA and Broadcom packages are cached with hashes for offline driver selection.
The GRUB hybrid image includes BIOS, UEFI and basic-graphics boot entries.

The pinned signed AmogOS archive supplies Installer, App Store, Music, Notes,
the persistent system package, updater and repository keyring. Installation tools
and Calamares fallback shortcuts belong to the live session. The persistent
system package retains the theme, credits and root-ownership guard after installation.
The live account is `user`; Debian live-config supplies its disposable live login.
Users choose their installed account through the installer.

The builder checks root:root 0755 before and after SquashFS creation. It enables
the root guard before tmpfiles, keeps normal APT recommendations for future apps,
and retains the signed AmogOS repository after installation. No private signing
key is needed or included. BIOS/UEFI support does not imply Secure Boot signing.

## Source and version policy

This is an ISO configuration/source build using upstream Debian binary packages
and pinned, authenticated AmogOS DEBs. It does not compile the Linux kernel,
Flutter SDK or every application from source. Application sources are available
at the exact revision recorded in `amogos-debian/sources.lock.json`.

The lock records package versions, bytes, SHA-256 values and the public keyring
hash. The fetched archive validates its signed indexes and package contents.
Debian repositories supply current Debian 13 package versions, so these are fresh
2.1 images, not byte-identical reproductions of an older published ISO. Each build
records its installed package inventory and source revision. Edit the lock and
package lists deliberately when updating the distribution.
Build-only APT preferences keep the locked AmogOS versions fixed while Debian
packages receive a full upgrade. Those preferences are removed before packing,
so installed systems continue receiving normal AmogOS updates.

## Development checks

```bash
python3 builder/cli.py --check
python3 -m unittest discover -s tests -v
```

After building, verify the image contents and optionally boot all four
firmware/media combinations with QEMU:

```bash
sudo python3 tools/verify_iso.py out/IMAGE.iso
sudo apt install qemu-system-x86 ovmf
sudo python3 tools/boot_test.py out/IMAGE.iso
```

The boot tests use disposable software-emulated VMs without network access or
writable host disks. Their JSON report records display-manager startup and
successful root-guard ordering before tmpfiles. On slow hosts, increase --timeout.
Recorded native build, image, boot and cleanup checks are in
[docs/verification.json](docs/verification.json), including their validation scope.

Each maintained code/configuration file has exactly one comment. Shell shebangs
count as that comment. JSON data, plain text assets, Markdown and empty tracking
files are exempt because they are not maintained code/configuration with comments.
The validation workflow enforces the convention and rejects private deployment paths.

Builder code is GPL-3.0-or-later. Project artwork and third-party assets retain
their existing provenance and licenses; see `shared/README.md`.
