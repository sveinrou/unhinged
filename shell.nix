{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    stdenv.cc.cc.lib
    zlib
    libjpeg
    libheif
  ];

  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
    echo "Unnghinged dev shell loaded."
    echo "Run: source .venv/bin/activate"
  '';
}
