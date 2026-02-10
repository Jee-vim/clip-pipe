with import <nixpkgs> {}; let
  pythonEnv = python3.withPackages (ps:
    with ps; [
      faster-whisper
      requests
      python-dotenv
      telethon
      ollama

      # YouTube upload
      google-api-python-client
      google-auth-oauthlib
      google-auth-httplib2
    ]);
in
  pkgs.mkShell {
    buildInputs = [
      python3
      pythonEnv

      yt-dlp
      ffmpeg
    ];
  }
## install nix on windows using wsl2
# wsl --install
# curl -L https://nixos.org/nix/install | sh
# nix-shell

