# Dead God Helper Save Extractor for Repentance+

A save file extractor for **The Binding of Isaac: Repentance+**, built for use with the [Dead God Helper](https://steamcommunity.com/sharedfiles/filedetails/?id=2985754961) mod.

> **Do you need this?** Probably not. The updated version of Dead God Helper, **DeadGod Helper: Reworked** (linked from the [original Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=2985754961)), imports your collection automatically if you have [Repentogon](https://repentogon.com/) installed. This extractor is only for players who **can't or don't want to install Repentogon**.

The extractor linked on Dead God Helper's Workshop page only reads **Repentance** saves. Repentance+ uses a different save format (`ISAACNGSAVE09R`), so the tool no longer works if on Repentance+.

It reads the collectibles you have already found and writes the files Dead God Helper needs, so the mod can flag items you haven't picked up on a given save, without everything starting out as "new".

## What it generates

| File | Goes in | Used by |
| --- | --- | --- |
| `saveX.dat` | `data/deadgod helper/` in the game folder | Dead God Helper |
| `eid_savegames.lua` | `mods/external item descriptions_836319872/scripts/` | External Item Descriptions (optional) |

`X` is the save slot number (1 to 3).

## Requirements

- Python 3.8 or newer. No extra packages.
- A Repentance+ persistent save file (`persistentgamedata*.dat`).
- [Dead God Helper](https://steamcommunity.com/sharedfiles/filedetails/?id=2985754961) installed in the game.

## Usage

```
python dgh_extractor.py path/to/persistentgamedata.dat slot [-o OUTDIR]
```

| Argument | Description |
| --- | --- |
| `path/to/persistentgamedata.dat` | Your Repentance+ save file |
| `slot` | The in-game save slot, `1`, `2` or `3` |
| `-o`, `--out` | Output folder (default: current folder) |

### Example

Slot 1, run from the `save-extractor` folder, writing to `./out`:

```
py dgh_extractor.py ..\persistentgamedata_real.dat 1 -o out
```

Output:

```
Items seen: 451/732
Wrote out\save1.dat and out\eid_savegames.lua
```

## Installing the output

1. Open the game folder.
   - Windows: `C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\`
   - Steam Deck / Linux: `~/.local/share/Steam/steamapps/common/The Binding of Isaac Rebirth/`
2. Create `data/deadgod helper/` if it doesn't exist. The game only creates it the first time the mod saves.
3. Copy `saveX.dat` into it. The slot number must match the slot you play on.
4. If you use EID, copy `eid_savegames.lua` into `mods/external item descriptions_836319872/scripts/` inside the game folder and overwrite the existing file (if applicable).
5. Copy the files **before** you pick up a new item in game. The mod writes its own save on the first new pickup and could overwrite yours.

On launch, the console (`~`) should print `DeadGod Helper loaded, N vanilla items seen`.

## Where to find your save file

- Windows: `Documents\My Games\Binding of Isaac Repentance+\persistentgamedata1.dat` (the exact folder and file name depend on your install)
- Steam Deck / Linux: `~/.local/share/Steam/userdata/<your id>/250900/remote/`

## How it works

The save file is a list of sections. The extractor walks the section headers from offset `0x14`, finds the collectibles section, and reads one byte per item ID (`1` for found, `0` for not). IDs 1 to 732 are written to the `seen` array in `saveX.dat`, which is the table Dead God Helper loads.

## Credits

- [Dead God Helper](https://steamcommunity.com/sharedfiles/filedetails/?id=2985754961) by Ayte. Source and the original Repentance extractor are on [forge.chapril.org](https://forge.chapril.org/ayte/DeadGodHelper).
- Save format research adapted from [jamesthejellyfish/isaac-save-edit-script](https://github.com/jamesthejellyfish/isaac-save-edit-script).
- The output file layout follows the original extractor, itself ported from [wofsauge/IsaacSavegameReader](https://github.com/wofsauge/IsaacSavegameReader).
