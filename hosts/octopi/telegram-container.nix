{ config, lib, pkgs, ... }:

let
  cfg = config.services.octopiTelegramJobs;
in
{
  options.services.octopiTelegramJobs.enable = lib.mkEnableOption "Docker and Compose for the Telegram jobs";

  config = lib.mkIf cfg.enable {
    virtualisation.docker.enable = true;
    environment.systemPackages = [ pkgs.docker-compose ];
  };
}
