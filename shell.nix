{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python3.withPackages (ps: [ ps.pyside6 ps.evdev ]);
  launcher = pkgs.stdenvNoCC.mkDerivation {
    pname = "wkeybutton-dev";
    version = "0.1.0";
    dontUnpack = true;
    nativeBuildInputs = [ pkgs.makeWrapper pkgs.qt6.wrapQtAppsHook ];
    buildInputs = [ pkgs.qt6.qtbase pkgs.qt6.qtwayland ];
    installPhase = ''
      mkdir -p "$out/bin"
      makeWrapper ${python}/bin/python "$out/bin/wkeybutton" \
        --add-flags "-m wkeybutton" \
        --prefix PYTHONPATH : ${pkgs.lib.escapeShellArg (toString ./.)} \
        --set QT_QPA_PLATFORM wayland
    '';
  };
in
pkgs.mkShell {
  packages = [ python launcher pkgs.acl ];
  shellHook = ''
    echo "Run: wkeybutton (or wkeybutton --dry-run to preview)"
  '';
}
