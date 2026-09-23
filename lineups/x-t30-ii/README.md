# X-T30 II: vintage film lineup

My Fujifilm X-T30 II setup: seven film-simulation recipes in custom slots C1–C7,
built around a vintage film look and a 1/4 mist filter. Everything the camera
holds is in the JSON files next to this README, so the whole setup can be put
back on the camera with one command.

Set up on 2026-09-22. Every slot was verified by reading it back from the camera.

## Files

| File | What it is |
|---|---|
| `lineup-mist.json` | **What is on the camera now.** C2, C4 and C5 use Clarity 0 for the mist filter. |
| `lineup.json` | The same lineup with each recipe's published Clarity, for shooting without the filter. |
| `previous-slots-2026-09-22.json` | What C1–C7 held before this lineup, read from the camera. Push it to restore the old setup. |

## The lineup

| Slot | Name on camera | Base | The look |
|---|---|---|---|
| C1 | REGGIES PORTRA | Classic Chrome | Warm, everyday Portra; handles mixed light. Made to be shot through a diffusion filter. |
| C2 | KODAK PORTRA 400 V2 MIST | Classic Chrome | Grainier, softer, more like a real Portra scan |
| C3 | KODACHROME 64 | Classic Chrome | Rich 1970s slide film |
| C4 | KODAK ROYAL GOLD 400 MIST | Classic Negative | Vivid 1990s drugstore-print colors, very saturated reds |
| C5 | PACIFIC BLUES MIST | Classic Negative | Cool, faded summer tones |
| C6 | CINESTILL 800T | Eterna | Tungsten cinema film, for night |
| C7 | KODAK TRI-X 400 | Acros +Y | Gritty classic black and white |

## Settings (camera menu order)

Generated from `lineup-mist.json`. Where the no-filter version differs, it is in brackets.

| Setting | C1 | C2 | C3 | C4 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|---|
| Film Simulation | Classic Chrome | Classic Chrome | Classic Chrome | Classic Negative | Classic Negative | Eterna | Acros Yellow |
| Grain Effect | Weak, Small | Strong, Small | Weak, Small | Strong, Small | Strong, Large | Strong, Large | Strong, Large |
| Color Chrome Effect | Strong | Strong | Strong | Strong | Strong | Strong | Strong |
| Color Chrome FX Blue | Weak | Weak | Weak | Strong | Strong | Strong | Off |
| White Balance | Auto | 5200K | Daylight | Shade | 5800K | Fluorescent 3 | Daylight |
| WB Shift | +2 R, -4 B | +1 R, -6 B | +2 R, -5 B | +3 R, +5 B | +1 R, -3 B | -6 R, -4 B | +9 R, -9 B |
| Dynamic Range | DR-Auto | DR400 | DR200 | DR400 | DR400 | DR400 | DR200 |
| D Range Priority | Off | Off | Off | Off | Off | Off | Off |
| Highlight | -1 | 0 | 0 | -1 | -2 | 0 | 0 |
| Shadow | -1 | -2 | 0 | +1 | +3 | +2 | +3 |
| Color | +2 | +2 | +2 | +4 | +4 | +4 | n/a |
| Monochromatic Color | n/a | n/a | n/a | n/a | n/a | n/a | WC 0, MG 0 |
| Sharpness | -2 | -2 | +1 | -1 | -2 | -3 | +1 |
| High ISO NR | -4 | -4 | -4 | -4 | -4 | -4 | -4 |
| Clarity | 0 | 0 (-2) | +3 | 0 (-3) | 0 (-3) | -5 | +4 |

The slots do not store ISO or exposure compensation. Set them when you switch recipes:

| Slot | ISO | Exposure compensation |
|---|---|---|
| C1 | Auto, max 6400 | Judge each shot; start around +1/3 to +1 |
| C2 | Auto, max 6400 | +1/3 to +1 |
| C3 | Auto, max 6400 | 0 to +2/3 |
| C4 | Auto, max 6400 | +1/3 to +2/3 |
| C5 | Auto, max 6400 | +2/3 to +1 |
| C6 | Auto, max 6400 | -1/3 to +2/3 |
| C7 | 1600–12800 | +1/3 to +1 |

## Notes on each recipe

- **C1 Reggie's Portra.** Its creator leaves Clarity at 0 and softens with a light
  diffusion filter instead, so it is the natural match for the mist filter.
- **C2 Portra 400 v2.** Why two Portras: Reggie's uses auto white balance and suits
  portraits and changing light. This one uses a fixed white balance with heavier
  grain and lower contrast, so it looks more like a film scan.
- **C3 Kodachrome 64.** If Color +2 feels like too much, +1 works, but reds and yellows
  get duller. Expect warm results indoors, since white balance is fixed to Daylight.
- **C4 Kodak Royal Gold 400.** Recreates the "memory colors" of 1990s and early-2000s
  prints. The most nostalgic look in the set.
- **C5 Pacific Blues.** Made for a sunny day at the beach. It turns warmer on overcast
  days and works well in fog and gray weather.
- **C6 CineStill 800T.** The night recipe. Its author is not fully happy with it: it
  looks accurate in some light and off in others. Alternatives that also work on the
  X-T30 II: Serr's 500T, Pushed CineStill 800T.
- **C7 Kodak Tri-X 400.** Acros +Y is saved; +R gives more dramatic skies, +G smoother
  skin. For lower contrast use Highlight -1, Shadow +2; for higher, +1 and +4. The high
  ISO range is intentional: Acros grain gets more natural as ISO rises.

## Shooting with the 1/4 mist filter

A mist filter softens detail and lowers contrast, which is what negative Clarity does.
Stacked, they get mushy, so the `MIST` versions of C2, C4 and C5 set Clarity to 0. They
also save the camera's pause after every shot that non-zero Clarity causes.

- **Best daytime match:** C1 Reggie's Portra.
- **Best at night:** C6 CineStill 800T. The filter's glow around streetlights and neon
  imitates the halation of real CineStill film.
- **C3 and C7** keep their positive Clarity; it offsets some of the softening.
- The effect shows most with bright light in or near the frame: backlight, sunsets,
  windows, streetlights. In flat light it barely shows.
- Try about 1/3 stop less exposure than the table above. The glow brightens highlights,
  and blown highlights look muddy through the filter.
- Without the filter, push `lineup.json` (or just `--slots 2 4 5`) to get the
  published Clarity back.

## Camera-wide settings

These are not part of any slot and cannot be set over USB; set them on the camera.

| Setting | Menu | Value | Why |
|---|---|---|---|
| Auto Update Custom Setting | IMAGE QUALITY SETTING, page 3 | DISABLE | Otherwise changing a setting while on a slot silently rewrites that recipe. |
| Auto mode selector lever | Lever beside the shutter-speed dial | Off Auto | In Auto the camera picks its own film simulation and Clarity, overriding the recipes. It also greys out the ISO menu. |
| Shutter Type | SHOOTING SETTING | MS+ES | Four slots use DR400, which needs ISO 640+. The electronic shutter goes past 1/4000 in bright sun. |
| Auto ISO presets | SHOOTING SETTING > ISO > AUTO | AUTO1: 160–6400, min shutter AUTO. AUTO2: 1600–12800 | AUTO1 for C1–C6, AUTO2 for Tri-X. |
| Natural Live View | SET UP > SCREEN SET-UP | OFF | The viewfinder shows the recipe's look. |
| Photometry | SHOOTING SETTING | Multi | Greyed out while Face/Eye Detection is on; the camera then meters for faces, which is fine. |
| Image Size / Quality | Each slot's EDIT/CHECK | L 3:2, FINE (+RAW optional) | RAW lets you re-render a shot with another recipe later. |
| Color Space | IMAGE QUALITY SETTING, page 3 | sRGB | What phones and the web expect. |

## Putting the lineup on the camera

1. On the camera: **MENU > SET UP > CONNECTION SETTING > CONNECTION MODE >
   USB RAW CONV./BACKUP RESTORE**. Turn the camera off, plug in the USB cable, turn it on.
2. From the repo root:

   ```bash
   .venv/bin/python manage.py camera_lineup verify lineups/x-t30-ii/lineup-mist.json
   .venv/bin/python manage.py camera_lineup push   lineups/x-t30-ii/lineup-mist.json
   .venv/bin/python manage.py camera_lineup push   lineups/x-t30-ii/lineup.json --slots 2 4 5
   .venv/bin/python manage.py camera_lineup import lineups/x-t30-ii/lineup.json   # database only
   ```

   `push` writes the recipes, then reads **every** slot back and compares it with the
   file. It exits non-zero if any slot differs.
3. Switch the connection mode back to your usual one before shooting.

The recipes also appear in the web app (Recipes page), where each one's description
carries its ISO and exposure notes. `import` adds them to a fresh database without
touching the camera.

## What went wrong, and the fixes

- **The camera reports errors for writes it applied.** On this body, a push can end
  with `Recipe write incomplete: ... ['DRangePriority', 'DRangeMode']` even though
  the slot reads back exactly right. The camera answers PTP `0x201C` for those
  properties. Trust the read-back, not the error. `camera_lineup` does this and shows
  the error only as a note.
- **A slot with D Range Priority on Auto cannot be fixed over USB.** The old C3 had
  D Range Priority = Auto. The camera rejected every write to it (Off, Weak, Strong,
  even Auto), and while it is not Off the slot also ignores Dynamic Range, Highlight
  and Shadow. The camera's own menu would not change it either. The fix: **IMAGE
  QUALITY SETTING > EDIT/SAVE CUSTOM SETTING > C1 > COPY > CUSTOM 3**, which copies a
  slot that has it Off over the stuck one, then push again. `camera_lineup` prints
  this hint when it sees the problem.
- **Menu path for editing a slot:** IMAGE QUALITY SETTING > EDIT/SAVE CUSTOM SETTING >
  (slot) > **EDIT/CHECK**. If red dots appear next to changed items, choose SAVE THE
  CHANGES.
- **Nothing outside the slots is reachable over USB.** In this connection mode the
  camera exposes the custom slots and the RAW-conversion settings only.
  `GetDevicePropDesc` is unsupported, and the Auto ISO properties do not answer.
  Camera-wide settings have to be set by hand.
- **Installing on macOS:** `./setup.sh lite` then `make setup-lite`. Homebrew's
  `libusb` and `exiftool` are the only system dependencies. macOS's `ptpcamerad` did
  not block the camera. Start the server from the repo root: the SQLite path is
  relative, so starting it elsewhere silently creates an empty database there.

Sources: [FUJIFILM X-T30 II Owner's Manual](https://fujifilm-dsc.com/en-int/manual/x-t30-2/index.html).
Recipes by Fuji X Weekly and their credited authors.
