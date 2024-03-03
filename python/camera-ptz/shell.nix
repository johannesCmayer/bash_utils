{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  # nativeBuildInputs is usually what you want -- tools you need to run
  nativeBuildInputs = with pkgs.buildPackages; [
    v4l-utils
    python39Full
    python39Packages.pygame
    python39Packages.typer
  ];
}
