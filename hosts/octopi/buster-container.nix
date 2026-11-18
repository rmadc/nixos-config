# Prepared for the Buster migration. Import this module only after the
# guest's network services and SSH service have been reviewed and disabled.
{ pkgs, ... }:
let
  printer = "/dev/serial/by-id/usb-marlinfw.org_Marlin_USB_Device_0F00300FAF4A10485D67AA23F50020C4-if00";
in
{
  environment.systemPackages = [ (pkgs.writeShellScriptBin "buster-shell" ''
    if [ "$(${pkgs.coreutils}/bin/id -u)" -ne 0 ]; then
      echo "Run buster-shell as root (for example: sudo buster-shell)." >&2
      exit 1
    fi
    leader="$(${pkgs.systemd}/bin/machinectl show octopi-buster -p Leader --value)"
    if [ -z "$leader" ] || [ "$leader" = 0 ]; then
      echo "The octopi-buster container is not running." >&2
      exit 1
    fi
    exec ${pkgs.util-linux}/bin/nsenter -t "$leader" --mount --uts --ipc --net --pid --root --wd -- \
      /usr/bin/env -i PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
      TERM="''${TERM:-xterm}" /bin/su - pi
  '') ];
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
