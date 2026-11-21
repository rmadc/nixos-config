{ ... }:

{
  # GRUB on the NVMe is the main menu; NixOS keeps its generation entries.
  boot.loader.systemd-boot.enable = false;
  boot.loader.timeout = 5;
  boot.loader.grub = {
    enable = true;
    efiSupport = true;
    device = "nodev";

    # Ubuntu and Windows keep their bootloaders on the eMMC EFI partition.
    # Search by filesystem UUID so partition renumbering does not break them.
    extraEntries = ''
      menuentry "Ubuntu (eMMC bootloader)" {
        insmod part_gpt
        insmod fat
        insmod search_fs_uuid
        insmod chain
        search --no-floppy --fs-uuid --set=root DA79-B56A
        chainloader /EFI/ubuntu/shimx64.efi
      }

      menuentry "Windows Boot Manager (eMMC)" {
        insmod part_gpt
        insmod fat
        insmod search_fs_uuid
        insmod chain
        search --no-floppy --fs-uuid --set=root DA79-B56A
        chainloader /EFI/Microsoft/Boot/bootmgfw.efi
      }
    '';
  };
}
