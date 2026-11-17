# Prepared for the Buster migration. Import this module only after the
# guest's network services and SSH service have been reviewed and disabled.
{ pkgs, ... }:
let
  printer = "/dev/serial/by-id/usb-marlinfw.org_Marlin_USB_Device_0F00300FAF4A10485D67AA23F50020C4-if00";
in
{
  systemd.services.octopi-buster = {
    description = "Debian Buster OctoPrint container";
    wantedBy = [ "multi-user.target" ];
    wants = [ "network-online.target" ];
    after = [ "network-online.target" ];
    unitConfig.RequiresMountsFor = [ "/var/lib/machines/octopi-buster" ];
    serviceConfig = {
      Type = "notify";
      ExecStart = "${pkgs.systemd}/bin/systemd-nspawn --quiet --keep-unit --boot --machine=octopi-buster --directory=/var/lib/machines/octopi-buster --private-users=no --bind=${printer}:/dev/ttyACM0";
      DeviceAllow = [ "/dev/ttyACM0 rw" ];
      KillMode = "mixed";
      Restart = "on-failure";
      TimeoutStopSec = "2min";
    };
  };
}
