#!/usr/bin/env python
"""Save extractor for Dead God Helper, for Repentance+ (ISAACNGSAVE09R) save files.

Usage: python dgh_extractor.py path/to/persistentgamedata.dat slot [-o OUTDIR]

Example (slot 1, from the save-extractor folder, output to ./out):
  py dgh_extractor.py persistentgamedata1.dat 1 -o out

Generates:
  - saveX.dat           -> Dead God Helper's data folder (data/deadgod helper/)
  - eid_savegames.lua   -> External Item Descriptions' scripts folder
"""
import argparse
import json
import sys
from pathlib import Path

HEADER = b"ISAACNGSAVE09R  "
FIRST_SECTION_OFFSET = 0x14
SECTION_HEADER_LEN = 12
# Bytes per entry for each section, in file order.
ENTRY_LENGTHS = [1, 4, 4, 1, 1, 1, 1, 4, 4, 1]
COLLECTIBLES_SECTION = 3  # zero-based index
MAX_ID = 732  # Matches save.settings.maxid in the mod


def read_collectibles(data):
    if data[:16] != HEADER:
        raise ValueError("Not a Repentance+ persistent save file (bad header).")
    offset = FIRST_SECTION_OFFSET
    for index, entry_len in enumerate(ENTRY_LENGTHS):
        count = int.from_bytes(data[offset + 8:offset + 10], "little")
        offset += SECTION_HEADER_LEN
        if index == COLLECTIBLES_SECTION:
            return list(data[offset:offset + count])
        offset += count * entry_len
    raise ValueError("Collectibles section not found.")


def seen_table(entries):
    """Index i of the result is item ID i+1 (what the mod expects)."""
    return [id_ < len(entries) and entries[id_] == 1 for id_ in range(1, MAX_ID + 1)]


def dgh_file(seen):
    # Same layout the mod writes: settings, seen, seenmodded.
    data = {
        "settings": {"visual": True, "eid": True, "showonmodded": True, "showonblind": False},
        "seen": seen,
        "seenmodded": {},
    }
    text = json.dumps(data, separators=(",", ":"))
    # The mod's JSON decoder needs seenmodded to stay an object.
    return text


def eid_file(seen, slot):
    lines = [
        "-- Auto generated from a python script",
        "if EID then",
        "\tEID.SaveGame = {}",
        '\tEID.SaveGame.Platform = "Steam"',
        '\tEID.SaveGame.UserID = "0"',
        '\tEID.SaveGame.UserName = "username"',
    ]
    for s in range(1, 4):
        mine = s == slot
        collected = ", ".join(
            f"[{i + 1}]={'true' if mine and v else 'false'}" for i, v in enumerate(seen))
        needs = ", ".join(
            f"[{i + 1}]={'true' if (not v) or not mine else 'false'}" for i, v in enumerate(seen))
        lines.append(f"\tEID.SaveGame[{s}] = {{")
        lines.append(f"\t\tItemCollection = {{\n\t\t\t{collected}\n\t\t}},")
        lines.append(f"\t\tItemNeedsPickup = {{\n\t\t\t{needs}\n\t\t}}")
        lines.append("\t}")
    lines.append("end")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("savefile")
    p.add_argument("slot", type=int, choices=[1, 2, 3])
    p.add_argument("-o", "--out", default=".", help="output directory (default: current)")
    args = p.parse_args()

    try:
        entries = read_collectibles(Path(args.savefile).read_bytes())
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    seen = seen_table(entries)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"save{args.slot}.dat").write_text(dgh_file(seen))
    (out / "eid_savegames.lua").write_text(eid_file(seen, args.slot))
    print(f"Items seen: {sum(seen)}/{MAX_ID}")
    print(f"Wrote {out / f'save{args.slot}.dat'} and {out / 'eid_savegames.lua'}")


if __name__ == "__main__":
    main()
