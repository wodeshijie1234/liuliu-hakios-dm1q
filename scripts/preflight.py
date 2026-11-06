#!/usr/bin/env python3
"""Read-only, public-safe inventory. This tool never unlocks or flashes a device."""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path

PUBLIC_KEYS = (
    'ro.product.manufacturer', 'ro.product.model', 'ro.product.device',
    'ro.soc.model', 'ro.bootloader', 'ro.build.PDA',
    'ro.build.version.release', 'ro.build.version.sdk',
    'ro.build.version.oneui', 'ro.build.version.security_patch',
    'ro.boot.flash.locked', 'ro.boot.vbmeta.device_state',
    'ro.boot.verifiedbootstate', 'ro.boot.warranty_bit', 'ro.boot.rp',
    'ro.boot.other.locked',
    'ro.boot.sales_code', 'ro.boot.slot_suffix',
    'ro.oem_unlock_supported', 'sys.oem_unlock_allowed',
)


def public_properties(properties):
    return {key: properties[key] for key in PUBLIC_KEYS if key in properties}


def evaluate(inventory, recovery):
    properties = inventory.get('properties', {})
    blockers = []
    if any(properties.get(key) != value for key, value in {
        'ro.product.model': 'SM-S9110',
        'ro.product.device': 'dm1q',
        'ro.soc.model': 'SM8550',
    }.items()):
        blockers.append('DEVICE_MISMATCH')
    files = recovery.get('files', {})
    if not all(role in files for role in ('BL', 'AP', 'CP', 'CSC')):
        blockers.append('RECOVERY_INCOMPLETE')
    if recovery.get('model') != 'SM-S9110':
        blockers.append('RECOVERY_MODEL_UNVERIFIED')
    try:
        if int(recovery['rollback_index']) < int(properties['ro.boot.rp']):
            blockers.append('ROLLBACK_INCOMPATIBLE')
    except (KeyError, ValueError, TypeError):
        blockers.append('ROLLBACK_UNVERIFIED')
    if not str(recovery.get('source_url', '')).startswith('https://'):
        blockers.append('RECOVERY_SOURCE_UNVERIFIED')
    for role in ('BL', 'AP', 'CP', 'CSC'):
        entry = files.get(role, {})
        path = Path(entry.get('path') or '/nonexistent-recovery-file')
        expected = entry.get('sha256', '')
        if not path.is_file() or not re.fullmatch(r'[0-9a-f]{64}', expected):
            blockers.append('RECOVERY_FILE_UNVERIFIED_' + role)
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            blockers.append('RECOVERY_HASH_MISMATCH_' + role)
    # This preflight never constitutes flash authorization or image validation.
    # The board's boot chain and recovery tool have not been exercised yet.
    blockers.append('DM1Q_BOOT_CHAIN_NOT_VALIDATED')
    return {'ready': not blockers, 'blockers': blockers}


def collect(adb):
    # Never run bare getprop, dumpsys telephony, account, SMS, or bugreport commands.
    state = subprocess.run([adb, 'get-state'], capture_output=True, text=True, timeout=15)
    if state.returncode or state.stdout.strip() != 'device':
        raise RuntimeError('Exactly one authorized ADB device is required; details suppressed.')
    properties = {}
    for key in PUBLIC_KEYS:
        result = subprocess.run([adb, 'shell', 'getprop', key],
                                capture_output=True, text=True, timeout=10)
        if result.returncode:
            raise RuntimeError('Cannot read allowlisted property: ' + key)
        properties[key] = result.stdout.strip()
    return {
        'schema_version': 1,
        'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source': 'live-adb-read-only',
        'properties': public_properties(properties),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default='adb')
    parser.add_argument('--inventory', type=Path,
                        help='Evaluate a saved inventory instead of using ADB')
    parser.add_argument('--recovery', type=Path,
                        help='Private recovery manifest with local file paths and hashes')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.inventory:
            inventory = json.loads(args.inventory.read_text())
            recovery = json.loads(args.recovery.read_text()) if args.recovery else {}
            report = evaluate(inventory, recovery)
        else:
            report = collect(args.adb)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, str(exc) + '\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Saved public inventory: ' + str(args.output))
    if args.inventory and not report['ready']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
