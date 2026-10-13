#!/bin/sh
# Build wvkbd-luna (Wyoh Step 6): Debian's wvkbd 0.15 source with Luna's
# AZERTY letter layer (keys_simple.luna.h) and the two-selection patch for
# gamepad typing (luna-cursors.patch). Run on a Debian 13 arm64 builder
# (luna-pi); Luna itself has no compiler. Prints the binary's SHA-256.
#
#   sh build_wvkbd_luna.sh [workdir]      (needs sudo for the build packages)
#
# The binary needs only libc >= 2.34, cairo, pango and wayland-client at run
# time, all present on Luna's ArchR image. Deploy it to
# /storage/.local/opt/wyoh-tools/bin/wvkbd-luna; it is not committed.
set -eu

VERSION=0.15
TARBALL="wvkbd_${VERSION}.orig.tar.xz"
URL="https://deb.debian.org/debian/pool/main/w/wvkbd/${TARBALL}"
SHA256="0b82a6497a1d886599d10695732dc3e4fac27eb8ca5d6469c27bd27b6c00e6f5"  # Debian wvkbd_0.15-1.dsc

HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${1:-"$HOME/build/wvkbd-luna"}

sudo apt-get install -y --no-install-recommends build-essential pkg-config wayland-protocols \
    libwayland-dev libxkbcommon-dev libcairo2-dev libpango1.0-dev curl xz-utils python3 patch

mkdir -p "$WORK"
cd "$WORK"
[ -f "$TARBALL" ] || curl -fsSLO "$URL"
echo "$SHA256  $TARBALL" | sha256sum -c -
rm -rf "wvkbd-${VERSION}"
tar xJf "$TARBALL"
cd "wvkbd-${VERSION}"
patch -p1 < "$HERE/luna-cursors.patch"

# layout.luna.h: the mobintl layouts with keys_simple[] replaced.
python3 - "$HERE/keys_simple.luna.h" <<'EOF'
import re, sys
from pathlib import Path
source = Path("layout.mobintl.h").read_text(encoding="utf-8")
start = source.index("static struct key keys_simple[] = {")
end = source.index("};", start) + 2
replacement = Path(sys.argv[1]).read_text(encoding="utf-8")
replacement = replacement[replacement.index("static struct key keys_simple[]"):]
Path("layout.luna.h").write_text(source[:start] + replacement.rstrip() + source[end:], encoding="utf-8")
EOF
cp keymap.mobintl.h keymap.luna.h
make LAYOUT=luna wvkbd-luna
./wvkbd-luna --version
sha256sum wvkbd-luna
