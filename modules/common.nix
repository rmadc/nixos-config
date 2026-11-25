# Settings shared by all hosts. Host-specific settings stay under hosts/<name>/.
{ pkgs, ... }:

{
  time.timeZone = "Europe/Madrid";

  # Configure network connections interactively with nmcli or nmtui.
  networking.networkmanager.enable = true;

  services.openssh.enable = true;

  # Required by scripts/deploy.sh for repository-managed deployments.
  # NixOS merges this list with each host's own package list.
  environment.systemPackages = [ pkgs.git ];
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
}
