#!/usr/bin/env python3

"""Look up the vendor of one or more MAC addresses using a local database."""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

DB_URL = 'https://maclookup.app/downloads/json-database/get-db?'
DB_MAX_AGE_DAYS = 30
SECONDS_PER_DAY = 24 * 60 * 60


def get_db_path():
    """Return the platform-specific database path."""
    if sys.platform.startswith('win'):
        base = os.environ.get('LOCALAPPDATA')
        base_path = Path(base) if base else Path.home() / 'AppData' / 'Local'
    else:
        base = os.environ.get('XDG_DATA_HOME')
        base_path = Path(base) if base else Path.home() / '.local' / 'share'
    return base_path / 'maclookup' / 'mac-vendors-export.json'


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Mac address vendor lookup.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-m', '--mac', nargs='+', type=str,
        help=(
            'Mac addresses to search. Accepted forms are: colon, dash, dot, '
            'whitespace or no separator (an optional 0x prefix is allowed). '
            'You can search for multiple mac separated by space. '
            'Example: python maclookup.py -m 11:22:33:44:55:66 '
            'aa-bb-cc-dd-ee-11 0016.9C11.1111 00169C111111'
        ),
    )
    group.add_argument(
        '-u', '--update', action='store_const', const=1,
        help=(
            'Download the last database version from '
            'https://maclookup.app/downloads/json-database/get-db?.'
        ),
    )
    return parser.parse_args()


def check_db_exist(db_path):
    """Download the database if it does not exist."""
    if not db_path.is_file():
        download_db(db_path)


def warn_if_db_old(db_path):
    """Print a warning if the database is older than the allowed age."""
    age_seconds = time.time() - db_path.stat().st_mtime
    if age_seconds <= DB_MAX_AGE_DAYS * SECONDS_PER_DAY:
        return
    age_days = int(age_seconds // SECONDS_PER_DAY)
    command = Path(sys.argv[0]).name
    print(
        f"Warning: the MAC vendor database is {age_days} days old. "
        f"Run '{command} -u' to update it.",
        file=sys.stderr,
    )


def load_db(db_path):
    """Load the vendor database from a JSON file."""
    with open(db_path, 'r', encoding="utf8") as file:
        return json.load(file)


def download_db(db_path):
    """Download the latest vendor database."""
    print('Downloading the latest MAC address database...')
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(DB_URL, headers=headers, timeout=30)

    if response.status_code == 200:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(db_path, 'wb') as file:
            file.write(response.content)
        print("Database downloaded successfully.")
    else:
        print(f"Failed to download database. Status code: {response.status_code}")
        sys.exit(1)


def normalize_mac(mac):
    """Return the MAC in canonical form or None if it is not valid."""
    value = mac.strip()
    if value[:2].lower() == '0x':
        value = value[2:]
    value = re.sub(r'[\s:.-]', '', value)
    if re.fullmatch(r'[0-9A-Fa-f]{12}', value) is None:
        return None
    value = value.upper()
    return ':'.join(value[i:i + 2] for i in range(0, len(value), 2))


def maclookup(db, maclist):
    """Print the vendor associated with each MAC address."""
    for raw_mac in maclist:
        mac = normalize_mac(raw_mac)
        if mac is None:
            print(f'Invalid MAC address format: {raw_mac}')
            continue
        try:
            matches = [i for i in db if mac.startswith(i['macPrefix'])]
            if matches:
                best_match = max(matches, key=lambda x: len(x['macPrefix']))
                vendor = best_match['vendorName']
                print(f'{mac} - {vendor}')
            else:
                print(f'{mac} - Vendor not found')
        except KeyError:
            print(f'{mac} - Vendor not found')


def main():
    """Run the MAC address vendor lookup."""
    args = parse_args()
    db_path = get_db_path()
    if args.update:
        download_db(db_path)
    else:
        check_db_exist(db_path)
        warn_if_db_old(db_path)
        db = load_db(db_path)
        maclookup(db, args.mac)


if __name__ == '__main__':
    main()
