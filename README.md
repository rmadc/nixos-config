# NixOS configuration

This repository is the source for `octopi`. Check it out at `/etc/nixos` on the Pi. The flake selects `hosts/octopi/configuration.nix`, which imports the hardware and Buster container modules.

Deploy the checked-out revision on the Pi:

```sh
sudo nixos-rebuild build --flake /etc/nixos#octopi
sudo nixos-rebuild switch --flake /etc/nixos#octopi
```

Inspect the active generation and the configuration commit used to build it:

```sh
readlink -f /run/current-system
nixos-version --configuration-revision
git -C /etc/nixos rev-parse HEAD
```

The active generation's revision is stored in `system.configurationRevision`. A value ending in `-dirty` means the build used uncommitted changes, so a commit alone cannot reproduce it.