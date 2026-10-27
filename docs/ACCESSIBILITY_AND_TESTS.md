# Accessibility validation and demo quality plan

This is a testing plan, not an accessibility certification.

## Core user journeys

**Audio-first supporter**: enter by keyboard or touch; start with sound intentionally off, enable speech, hear a concise statement of the ball situation, request more detail only if desired; pause or replay without losing place. The pitch must never be the only way to understand a major event.

**Partially sighted supporter**: quickly distinguish teams by **shape and colour**; locate white ball; use pitch plus text descriptions at adjustable density; avoid overlaid controls obstructing ball. Can change to audio-first without resetting sequence.

## Test questions for supporters

1. Without viewing the pitch, can the supporter identify who has possession, in which general area and what happened at the shot?
2. With low vision, can the supporter find the ball and distinguish the two teams within 3 seconds at normal display scale?
3. Are descriptions too sparse or too busy? Can the supporter choose an appropriate level?
4. Does audio make sense in time with the event? What is confusing at half speed or after seeking?
5. Is event selection, pause and restart usable using the individual's normal assistive technology?

## Structured QA

- Browser keyboard: Tab through mode controls, Play, Restart, Seek, Speed, Detail, Voice, Narration, event list. Press Shift+Tab to reverse. Focus remains visible.
- Screen readers: VoiceOver on iPhone/macOS, NVDA on Windows, TalkBack on Android if available. Ensure announcement only when an event changes; avoid repeated frame-by-frame status announcements. Pitch has a static accessible summary; text is the event-by-event alternative.
- Audio: test built-in `speechSynthesis`, browser autoplay restrictions and actual audio overlaps. Confirm speech is off until explicit activation and cancels on Pause or Restart.
- Vision: zoom to 200% and 400%, high contrast and reduced motion; compare colours in simulated colour-vision deficiencies; use native text sizing.
- Data: run Python continuity suite and check all 22 players, 401 frames, bounded pitch, pass origin/arrival, ball/player speed, sorted events, explicit no-goal result.
- Integrity: sample 12 events, seek through all, compare on-screen text to corresponding JSON `narration`/`why`. Deliberately try to force an unsupported score/goal through the Azure adapter and confirm rejection.
- Browser: desktop Chromium + mobile viewport smoke test performed locally on 19 October 2026 using in-memory Playwright execution. Direct automated HTTP navigation is restricted in the test environment, but Node route tests and Chromium DOM interactions passed.

## Target thresholds for a later real AI test (hypotheses, not proven)

- Event claim accuracy: **zero unsupported named player, goal, score or card claims** across a held-out synthetic fixture.
- End-to-end AI narration generation after event confirmation: target **p95 <= 2.0 seconds**; measure rather than assume.
- Speech overlap: none; clearly announce skipped/queued content when events arrive faster than TTS.
- User comprehension: participants can correctly describe at least 4 of 5 key moments without visual access after one replay. Two to five testers are useful formative feedback but are not a statistically representative sample.
- Keyboard and screen reader: no blocking interactions on target devices.

## Stop/pivot criteria

- If users cannot follow the play from audio alone, rework event selection and timing before adding more features.
- If TTS cannot keep up with the pace, prioritise high-information changes and summarize rather than narrate every event.
- If live Foundry output cannot be reliably grounded, ship only the deterministic narrative as a labelled fallback and **do not claim AI explanation is trustworthy**.
