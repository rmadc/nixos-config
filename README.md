# NixOS configuration

This repository can hold configurations for multiple NixOS hosts. The commands
below use `octopi` as an example and are run on that Pi unless otherwise stated.
Its flake entry selects `hosts/octopi/configuration.nix`, which imports the
hardware and Buster container modules and enables Docker and Compose.

## First checkout

On a host where `/etc/nixos` does **not** already exist, clone the repository:

```sh
sudo git clone https://github.com/rmadc/nixos-config.git /etc/nixos
```

A normal NixOS installation already has an `/etc/nixos` directory. Inspect and
back up that directory before replacing it with a checkout; cloning into a
non-empty directory will fail. Do not overwrite its configuration blindly. This
repository's `octopi` hardware configuration is specific to that machine; a
new host needs its own hardware configuration and flake entry.

The current `octopi` already has the repository checked out at `/etc/nixos`;
do not clone it again. Git commands below use `sudo` because that checkout is
owned by root.

## Adopt the checkout on raptop

`raptop` adopted the checkout on 2026-11-25. Its installer-generated files are
kept in `/etc/nixos.pre-flake`. They are older than this repository's
configuration: they select systemd-boot instead of GRUB, so do not rebuild the
system from them. The steps below record the one-time adoption, for reference or
for a similar host. Do not repeat them on `raptop`.

Move the old directory aside and clone the repository:

```sh
sudo mv /etc/nixos /etc/nixos.pre-flake
sudo git clone https://github.com/rmadc/nixos-config.git /etc/nixos
```

Build and preview without activating. Run the build outside the checkout: it
creates a `result` link in the current directory.

```sh
cd /tmp
sudo nixos-rebuild build --flake /etc/nixos#raptop
nix store diff-closures /run/current-system ./result
sudo nixos-rebuild dry-activate --flake /etc/nixos#raptop
```

After reviewing the output, deploy with the script described below. Keep
`/etc/nixos.pre-flake` until the deployed system has survived a reboot.

## Update and deploy

For example, on `octopi`, run:

```sh
sudo /etc/nixos/scripts/deploy.sh
```

The script checks that the checkout has no uncommitted or untracked changes,
then pulls the current branch with `git pull --ff-only`. It stops if the pull
fails. It prints the resulting commit and runs `nixos-rebuild switch`; the
system is built before activation, and a failed build stops the deployment.
Review upstream changes before running it because it deploys the latest commit
on the current branch automatically.

The script works out the repository location from its own path and selects the
flake configuration using the machine's short hostname. For example, on
`octopi` it deploys `nixosConfigurations.octopi`. Each machine needs a matching
entry in `flake.nix`. For a checkout elsewhere, use that checkout's script path.
If the checkout has local changes or the pull cannot fast-forward, inspect and
resolve that state before continuing.

When upgrading from a checkout that has the older script without automatic
pulling, pull once manually before using the command above:

```sh
sudo git -C /etc/nixos pull --ff-only
```

## Check what is running

```sh
readlink -f /run/current-system
nixos-version --configuration-revision
sudo git -C /etc/nixos rev-parse HEAD
```

The running generation records its configuration commit in
`system.configurationRevision`. Compare it with the checkout's `HEAD` to check
whether the current checkout is deployed. A revision ending in `-dirty` means
the build used uncommitted changes and cannot be reproduced from a commit
alone.

## Containers

The Buster installation runs as the `octopi-buster` systemd-nspawn service.
NixOS enables Docker; OctoPrint and the Telegram jobs are managed separately
with Docker Compose. `deploy.sh` pulls and applies NixOS configuration only:
it does **not** build or apply either Compose project. Existing containers start
after boot via Docker's `unless-stopped` policy.

- [Octopi operations, migration and recovery](docs/octopi-operations.md)
- [OctoPrint Compose and migration notes](containers/octoprint/README.md)
- [Telegram jobs, data and secrets](containers/telegram/README.md)
- [Portainer web UI for Docker](containers/portainer/README.md)
- [DockGraph topology viewer](containers/dockgraph/README.md)
