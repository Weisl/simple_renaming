#!/usr/bin/env bash
#
# Test the addon in a Blender profile fully isolated from your normal one.
#
# BLENDER_USER_RESOURCES is redirected to a private directory, so installing
# the addon, enabling it, or any preference/keymap changes made during the
# test session never touch your real ~/.config/blender/<version>/ profile.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GITHUB_REPO="Weisl/simple_renaming"
DEFAULT_PROFILE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/simple_renaming_blender_test"

usage() {
  cat <<EOF
Usage: $(basename "$0") --blender PATH (--build | --zip FILE | --release [TAG]) [options]

Launches Blender against a profile isolated from your normal one, with the
addon installed and enabled, so testing never touches your real settings,
addons, or hotkeys.

Required:
  --blender PATH     Path to the Blender executable to test against.
                      (or set \$BLENDER_BIN)

Addon source (choose exactly one):
  --build             Package the working tree via
                      'blender --command extension build'.
  --zip FILE          Install this local extension zip as-is.
  --release [TAG]     Download a release asset from GitHub ($GITHUB_REPO).
                      Omit TAG to use the latest release. Requires 'gh'.

Options:
  --profile-dir DIR   Isolated profile directory.
                      Default: $DEFAULT_PROFILE_DIR
  --reset             Wipe the profile directory first (true factory state).
  --no-launch         Install only; don't open the Blender GUI afterwards.
  -h, --help          Show this help.
EOF
}

BLENDER_BIN="${BLENDER_BIN:-}"
PROFILE_DIR="$DEFAULT_PROFILE_DIR"
SOURCE_MODE=""
ZIP_ARG=""
RELEASE_TAG=""
RESET=0
NO_LAUNCH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --blender)
      BLENDER_BIN="$2"; shift 2 ;;
    --build)
      SOURCE_MODE="build"; shift ;;
    --zip)
      SOURCE_MODE="zip"; ZIP_ARG="$2"; shift 2 ;;
    --release)
      SOURCE_MODE="release"; shift
      if [[ $# -gt 0 && "$1" != -* ]]; then
        RELEASE_TAG="$1"; shift
      fi
      ;;
    --profile-dir)
      PROFILE_DIR="$2"; shift 2 ;;
    --reset)
      RESET=1; shift ;;
    --no-launch)
      NO_LAUNCH=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$BLENDER_BIN" ]]; then
  echo "Error: --blender PATH is required (or set \$BLENDER_BIN)." >&2
  exit 1
fi
if [[ ! -x "$BLENDER_BIN" ]]; then
  echo "Error: '$BLENDER_BIN' is not an executable file." >&2
  exit 1
fi
if [[ -z "$SOURCE_MODE" ]]; then
  echo "Error: choose one of --build, --zip, or --release." >&2
  exit 1
fi

if [[ $RESET -eq 1 ]]; then
  echo "Resetting profile: $PROFILE_DIR"
  rm -rf "$PROFILE_DIR"
fi
mkdir -p "$PROFILE_DIR"
export BLENDER_USER_RESOURCES="$PROFILE_DIR"
echo "Isolated profile: $PROFILE_DIR"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

ZIP=""
case "$SOURCE_MODE" in
  build)
    echo "Building extension package from $REPO_ROOT ..."
    "$BLENDER_BIN" --command extension build \
      --source-dir "$REPO_ROOT" \
      --output-dir "$WORK_DIR"
    ZIP="$(find "$WORK_DIR" -maxdepth 1 -name '*.zip' | head -1)"
    ;;
  zip)
    ZIP="$ZIP_ARG"
    ;;
  release)
    echo "Fetching release ${RELEASE_TAG:-<latest>} from $GITHUB_REPO ..."
    command -v gh >/dev/null 2>&1 || { echo "Error: 'gh' CLI is required for --release." >&2; exit 1; }
    gh release download $RELEASE_TAG --repo "$GITHUB_REPO" --pattern '*.zip' --dir "$WORK_DIR" --clobber
    ZIP="$(find "$WORK_DIR" -maxdepth 1 -name '*.zip' | head -1)"
    ;;
esac

if [[ -z "$ZIP" || ! -f "$ZIP" ]]; then
  echo "Error: could not resolve an extension zip to install." >&2
  exit 1
fi
echo "Installing: $ZIP"

# --factory-startup here just keeps the background install from picking up any
# startup.blend saved into the profile by an earlier interactive test session.
"$BLENDER_BIN" --background --factory-startup --command extension install-file \
  --repo user_default --enable "$ZIP"

if [[ $NO_LAUNCH -eq 1 ]]; then
  echo "Installed. Skipping launch (--no-launch)."
  exit 0
fi

# No --factory-startup here: it would also skip loading installed extensions,
# so the addon would show as disabled. The isolated profile alone gives a
# clean session; use --reset for a true from-scratch state.
echo "Launching Blender (isolated profile, addon enabled) ..."
exec "$BLENDER_BIN"
