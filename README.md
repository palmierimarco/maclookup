# MAC Address Vendor Lookup

This Python script allows you to look up the vendor for one or more MAC addresses using a local database file. You can also update the database from [maclookup.app](https://maclookup.app/downloads/json-database).

## Requirements

- Python 3.x
- `requests` library

Install dependencies (if needed):

```sh
pip install requests
```

## Usage

### Lookup MAC Addresses

You can look up one or more MAC addresses. All common formats are accepted, including colon, dash, dot, whitespace, no separator and an optional `0x` prefix:

```sh
python maclookup.py -m 00:16:9C:11:11:11 aa-bb-cc-dd-ee-11 0016.9C11.1111
python maclookup.py -m 00.16.9C.11.11.11 00169C111111 0x00169C111111
python maclookup.py -m "00 16 9C 11 11 11"
```

### Update the Database

To download the latest vendor database:

```sh
python maclookup.py -u
```

## Output

For each MAC address, the script prints the vendor name if found, or "Vendor not found" otherwise.

Example:

```
00:16:9C:11:11:11 - Cisco Systems, Inc
AA:BB:CC:DD:EE:11 - Vendor not found
```

## Files

- `maclookup.py`: Main script.
- `mac-vendors-export.json`: Local vendor database (downloaded/used by the script).

## Notes

- Supported MAC address formats: colon (`:`), dash (`-`), dot (`.`), whitespace, no separator, with an optional `0x` prefix.
- The script selects the vendor with the longest-match mac address.
- The database is stored in the user data folder:
  - Linux: `${XDG_DATA_HOME:-~/.local/share}/maclookup/mac-vendors-export.json`
  - Windows: `%LOCALAPPDATA%\maclookup\mac-vendors-export.json`
- If the database is older than 30 days, the script prints a warning suggesting to run `-u` to update it.

## Releases

Pushing a commit to `main` with `[build]` in the message builds the Linux and Windows executables and publishes them as a GitHub Release. The commit message must also contain a semantic version, for example:

```sh
git commit -m "Release [build] v1.2.3"
git push origin main
```

The release is published with tag `v1.2.3` and the versioned executables as assets.

You can also run the workflow manually from the **Actions** tab (`Build` → **Run workflow**), providing the version number as input. In that case no `[build]` marker is needed.

## Compatibility

- **Linux:** Fully supported. The release binary is built on Ubuntu 22.04 and requires glibc 2.35 or newer.
- **Windows:** Fully supported. You can use the .exe file without install python.
