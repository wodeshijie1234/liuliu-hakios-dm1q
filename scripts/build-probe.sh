#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${ZIG:?Set ZIG to an installed, verified zig compiler path}"
mkdir -p build/cache build/global-cache
export ZIG_LOCAL_CACHE_DIR="$PWD/build/cache"
export ZIG_GLOBAL_CACHE_DIR="$PWD/build/global-cache"
"$ZIG" build-exe src/uefi_probe.c -I third_party/hakios \
    -target aarch64-uefi -O ReleaseSmall \
    -fno-stack-protector -fno-stack-check -femit-bin=build/dm1q-uefi-probe.efi
file build/dm1q-uefi-probe.efi
shasum -a 256 build/dm1q-uefi-probe.efi
printf '%s\n' 'Built only. Not flashed or executed on hardware.'
