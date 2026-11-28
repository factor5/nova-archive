# Spice Run (*Dune*)

The pilot book game. General rules, the shell and the process are in [`../README.md`](../README.md).

## 1. Overview
| | |
|---|---|
| Book | *Dune*, Frank Herbert (`dune--frank-herbert`; Hugo 1966, Nebula 1965) |
| Game | Spice Run, top-down survival, endless score run |
| Slug | `dune` |
| Status | beta (behind "Show games (beta)") |
| Code | `js/games/dune.js` |
| Frame | `css/games/dune.css` |
| Tests | `tests/features/13-games.feature` (section 8) |

## 2. Plot moments (approved by the author, 2026-11-28)
Drafted from the Wikipedia plot section of *Dune* (novel) in our own words; no names, generic terms for places and peoples ("the desert planet", "the desert people").

**Source quality:** the plot section is complete (about 8,500 characters) but focused on politics. Sandworms guarding spice, the escape into a sandstorm and spice visions are covered. "Walking without rhythm" is supported only indirectly (a song reference in the article's Cultural influence section); the author confirmed it fits the book. Thumpers, stillsuits and spice blows are not on the page.

| # | Moment | Use in the game |
|---|---|---|
| 1 | After a betrayal, the heir of a noble house and his mother flee into the open desert; a sandstorm hides them from their pursuers. | Intro line: why the storm is behind you |
| 2 | In the deep desert spice is concentrated enough to bring visions; it is the most valuable substance there is. | What you collect; later maybe "vision" lines at score milestones |
| 3 | Giant sandworms make harvesting spice deadly. | The worm; game-over "Taken by the worm" |
| 4 | Desert people walk without rhythm so the worm does not sense them. | The noise rule; the worm tip |
| 5 | The desert people take the fugitives in; in the end they ride giant sandworms into battle. | Not now. Candidate twist (ride the worm) only if the core loop sticks |

## 3. Text in the game
In `meta` at the top of `js/games/dune.js`.

- **Intro** (start screen, from moments 1 and 3): "Betrayed and hunted, you have fled into the deep desert. The storm that hid you is still at your back, and something vast moves under the sand."
- **How to play** (start screen): drag anywhere to move (keyboard: arrows or WASD, Shift to run); the further you drag, the faster and louder you are; noise draws the worm; the storm moves in from the top and spice pushes it back.
- **Tips** (game-over screen, one per way of losing):
  - *Taken by the worm* (moment 4): "Tip: the desert people walk without rhythm. Slow, soft steps do not carry through the sand, so stay inside the inner ring when the worm is near."
  - *Lost in the storm*: "Tip: every spice you gather pushes the storm back. Creeping keeps you safe from the worm, but not from the storm."

The plan was one tip line; there is one per way of losing because each needs different advice.

## 4. Design sheet
- **Goal:** collect as much spice as possible before being caught.
- **Core tension (greed vs noise):** moving fast makes noise, and noise draws the sandworm. Moving slowly is quiet, but the storm closes in, so you cannot just creep.
- **World:** the shorter side of the play area is always 360 units, so the game feels the same on any screen. Turning the phone scales every position with the screen.
- **Controls (touch):** a floating joystick. Put a thumb down anywhere and drag; how far you drag sets speed, and speed is noise. Full speed at 110 px of drag (about 18 mm on the reference phone), nothing within 8 px, and a curved response (speed = drag^1.6), so the silent walking range is about 60 px (about 10 mm). An inner ring on the joystick marks the silent range. Once the thumb passes the edge, the base follows it, so changing direction is immediate.
- **Controls (keyboard):** arrow keys or WASD walk silently; hold Shift to run.
- **Noise:** rises quickly with speed and fades slowly; silent below 35% of full speed. Above the hearing level the meter turns dark and reads "NOISE: LOUD, the worm hears you".
- **Worm:** roams at 35 units/s. When it hears you it heads for the place it last heard you, hunting at 58, up to 105 at full noise (you run at 140). It speeds up gradually (40 units/s per second) and turns at a limited rate, so a sidestep can save you. When it reaches the last place it heard you and hears nothing, it goes back to roaming.
- **Storm:** a band that moves in from the top and speeds up with difficulty. Each spice pushes it back 28 units.
- **Spice:** 4 on the sand at a time, a new one shortly after each pickup, never right next to you, never inside the storm.
- **Lose:** the worm reaches you ("Taken by the worm"), or the storm covers you ("Lost in the storm").
- **Score:** spice collected. Best score kept locally.
- **Difficulty:** rises over 2 minutes to 1.8× (worm speed and turning, storm speed).
- **Feedback:** noise meter with a hearing-level mark; rings around the worm's head (three while hunting); a ridge of sand trailing the worm; a striped storm band with a ragged front.
- **Art:** shapes on a sand palette. Danger is shown by shape and motion, not only colour (rings, stripes, the LOUD label). No screen shake with reduced motion.

## 5. Decorative frame
`css/games/dune.css`, loaded only when the game opens. CSS and inline SVG only.
- Palette: dark rust, spice orange, gold and sand.
- Top bar: a banner with a gold rule and a dune-wave edge; the title in serif capitals between spice diamonds.
- Play area: a diamond-chain border (gold diamonds with spice centres on dark rust), a gold inner rule, and an eight-point star in each corner.
- Panels: parchment with a gold and rust double rule, three spice diamonds above the title, rust buttons.

## 6. Tuning
All values are in the `C` block at the top of `js/games/dune.js` (world units and seconds; joystick values in screen pixels).

| Area | Values |
|---|---|
| Player | `maxSpeed` 140, `quietBelow` 0.35 |
| Noise | `noiseUp` 2.5, `noiseDown` 0.6, `hearAt` 0.3 |
| Worm | `wormRoam` 35, `wormHunt` 58, `wormHuntLoud` 47, `wormAccel` 40, `wormBrake` 80, `wormTurn` 2.2 |
| Storm | `stormSpeed` 9, `stormPush` 28 |
| Spice | `spiceCount` 4, `pickup` 15, `respawn` 0.6 |
| Difficulty | `rampSeconds` 120, `maxDiff` 1.8 |
| Joystick | `joyR` 110, `joyDead` 8, `joyCurve` 1.6 |

## 7. Playtest log
| Round | Feedback | Change | PR |
|---|---|---|---|
| 1 | "The touch control is too unresponsive; it's almost impossible to move slow." | Joystick radius 60 → 110 px, dead zone, curved response (silent range about 3.5 → 10 mm); base follows the thumb; inner ring | #12 |
| 2 | "The worm starts moving too fast when it detects me." | Hunt speed 70–130 → 58–105; gradual speed-up instead of a jump | #13 |
| — | "It feels OK now." Stop rule passed. | Intro line and tips; decorative frame; turning the phone mid-run fixed | this PR |

## 8. Game-specific tests
In `tests/features/13-games.feature` (the rest of that file covers the shared shell):
- GM-09: the keyboard moves the player.
- GM-10: dragging moves the player, and a long drag makes noise.
- GM-11: a full run (fixed seed, 3× speed) collects spice, ends, and keeps the best score.
- GM-16: changing direction after a long drag is immediate (the base follows the thumb).
- GM-18: turning the phone mid-run keeps the game going.
- GM-14 (manual): the playtest checklist on the phone.
