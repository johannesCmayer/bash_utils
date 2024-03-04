{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  # nativeBuildInputs is usually what you want -- tools you need to run
  nativeBuildInputs = with pkgs.buildPackages; [
    v4l-utils
    python311Full
    python311Packages.pygame
    python311Packages.typer
  ];
}
