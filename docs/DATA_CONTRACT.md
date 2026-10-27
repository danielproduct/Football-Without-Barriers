# Synthetic data contract v0.2

## Provenance and output

- Generated from original fictional keyframes and event scripts with `python3 tools/generate_match.py`.
- Data assets: `public/data/match.json` (canonical), `public/data/match.js` (in-browser no-fetch mirror).
- 105m x 68m pitch, origin **top left**; X increases left-to-right; Y increases top-to-bottom; home attacks increasing X.
- Time unit is `t_ms`, milliseconds from start of **fictional passage**, not real match clock.
- Every synthetic frame has 22 identifiable players plus an independent ball position. 80 seconds at 5 frames/s = 401 frames.

## Top-level `match.json`

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | `0.2` |
| `match_id` | string | stable fictional ID |
| `synthetic` | bool | must always be true |
| `provenance` | string | no real-match provenance |
| `title` | string | demo name |
| `duration_ms` | integer | 80000 |
| `fps` | integer | 5 |
| `pitch` | object | length/width/coordinate system |
| `teams` | array | home and away labels and orientation |
| `players` | array | `id`, `team_id`, `number`, `name`, `role` |
| `frames` | array | timestamped ball, possession and player positions |
| `events` | array | event explanations with timestamp/evidence |
| `result` | object | explicit 0-0; partial sequence only |

## Tracking frame schema

```json
{"t_ms":0,"ball":{"x":32.0,"y":31.0},"possession":{"team_id":"home","player_id":"H6"},"players":[{"id":"H1","x":4.0,"y":34.0}]}
```

The `players` array shown is shortened for illustration; each real frame contains **22** records. Coordinates use metres with no inverted axis or hidden implicit mapping. `possession` may be null in flight or when not established. This is unlike some real commercial feeds, which may have coverage gaps and confidence flags; the fictional demo has no source-detection uncertainty.

## Event schema

```json
{"id":"E01","t_ms":9000,"kind":"pass","team_id":"home","player_id":"H6","recipient_id":"H8","outcome":"complete","priority":2,"location_m":{"x":38,"y":31},"facts":{"nearest_opponent_id":"A10","nearest_opponent_distance_m":20,"forward_progress_m":11,"confirmed_goal":false},"narration":{"essential":"Hart passes to Imani.","detailed":"Hart moves the ball forward to Imani..."},"why":"The pass advances the ball...","evidence":{"frame_t_ms":9000,"source":"original synthetic frames and authored events"}}
```

**Important:** example numeric values here illustrate *shape only*; authoritative values are in the generated JSON. `nearest_opponent_distance_m` is a simple Euclidean proximity calculation; it is not a vendor-certified pressure metric. `forward_progress_m` uses X displacement in the home-attacking direction; do not apply to away attacks without transforming sign.

**Causal replay timing (v0.2):** `observed_at_ms` / `t_ms` records action initiation; `resolved_at_ms` marks the first sampled frame demonstrating the result; `available_at_ms` is the earliest time a confirmed result may be shown or narrated. The UI gates outcome text, event list navigation, and completed-event counters on `available_at_ms`. `evidence.observation_frame_t_ms` records launch; `evidence.frame_t_ms` records the confirmatory sample. The fixture remains a *pre-scripted replay* and does **not** claim real-time predictive validity or a live model.

For example, E01 is initiated at 9000ms and its completed-pass text cannot appear before 10200ms; the shot result E08 cannot appear before 61600ms.

## Mapping to public reference formats (research only)

| Our contract | Metrica Sports public CSV | SkillCorner open tracking JSONL |
|---|---|---|
| `t_ms` | `Start Time [s]`, `Start Frame` | `timestamp`, `frame` |
| `kind` | `Type`, `Subtype` | separate `dynamic_events.csv` |
| `team_id` | `Team` | `possession.group` or lineup association |
| `player_id` | `From` | `player_data[].player_id` |
| `recipient_id` | `To` | derived events |
| event X/Y | `Start X`, `Start Y` normalised 0..1 | metres from pitch centre |
| `frames[].players[].x/y` | team tracking CSV coordinates 0..1 | player X/Y in metres |
| `frames[].ball` | tracked ball X/Y | `ball_data` object |

**Normalization:** Metrica 0..1 → X*105, Y*68; SkillCorner uses pitch-centred coordinates; our top-left convention is `x_ours=x_sc+52.5`, `y_ours=y_sc+34` if axis orientation agrees. Always validate vendor orientation before using the mapping; frame origin and team attacking direction may change.

## Remaining future gates

1. Separate **provisional** launch announcements from later confirmed outcomes if required for a genuine streaming system. The current minimal replay waits until confirmation before playing an event's full description.
2. Track source-quality and uncertainty scores only when a real model/data source can justify them.
3. Implement structured claims and evidence pointers with deterministic validation before any Azure narration can be labelled evidence-checked.
4. Evaluate end-to-end narration delay and multiple matches, not just one synthetic passage.
