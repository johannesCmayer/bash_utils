# I don't get how to do this.
import ./shell.nix

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  shellHook = ''
    python camera-ptz.py
  '';
}
