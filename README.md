# NixOS configuration

This repository is the source for the `octopi` NixOS host. Its flake selects
`hosts/octopi/configuration.nix`, which imports the hardware, Buster container,
and Docker configuration modules. Commands below are run on the Pi unless
otherwise stated.

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

Check for local changes before pulling:

```sh
sudo git -C /etc/nixos status --short --branch
```

If the checkout is clean, retrieve the latest committed changes and build the
configuration without activating it:

```sh
sudo git -C /etc/nixos pull --ff-only
sudo nixos-rebuild build --flake /etc/nixos#octopi
```

If the build succeeds, activate that configuration:

```sh
sudo nixos-rebuild switch --flake /etc/nixos#octopi
```

If the checkout has local changes or the pull cannot fast-forward, inspect and
resolve that state before continuing. `switch` changes the running host; review
the commit and its effects before deploying it.

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
