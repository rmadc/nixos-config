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

## Update and deploy

Review the latest commit and check that your checkout is clean before pulling.
The existing `octopi` checkout is owned by root, so use:

```sh
sudo git -C /etc/nixos status --short --branch
sudo git -C /etc/nixos pull --ff-only
```

Then review the pulled changes and deploy the checked-out revision:

```sh
sudo /etc/nixos/scripts/deploy.sh
```

The script works out the repository location from its own path and selects the
flake configuration using the machine's short hostname. For example, on
`octopi` it deploys `nixosConfigurations.octopi`. Each machine needs a matching
entry in `flake.nix`. The script refuses uncommitted or untracked changes,
prints the revision, and runs `nixos-rebuild switch`; it builds the system
before activation and stops if the build fails. It does not pull changes.

If the checkout has local changes or the pull cannot fast-forward, inspect and
resolve that state before continuing. Deploying changes the running host; review
the commit and its effects first. For a checkout elsewhere, use the path to
that checkout's `scripts/deploy.sh` instead.

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
The Docker and Compose configuration is declarative; the Telegram Compose
project remains a draft and does not start automatically when NixOS is
rebuilt. See [the Telegram draft README](containers/telegram/README.md) for
its files, volumes, secrets and outstanding validation before cutover.
