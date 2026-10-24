## 1. Theme Foundation

- [x] 1.1 Refactor the review page's theme-sensitive color literals into semantic CSS tokens, define matching dark and light token sets, and verify all documented workspace surfaces render legibly in each theme.
- [x] 1.2 Update canvas, overlay, hover, selected, keep, drop, and status styling to consume theme-aware values, and verify transcript selection, playback highlighting, waveform display, and export status remain distinguishable in both modes.

## 2. Theme Preference Interaction

- [x] 2.1 Add an accessible two-state theme toggle to the review toolbar with accurate visible text, title, and ARIA state, and verify keyboard activation switches immediately between light and dark modes.
- [x] 2.2 Implement validated theme initialization and guarded `localStorage` persistence using a namespaced preference key, and verify first visit defaults to dark while a later reload restores a saved light selection.
- [x] 2.3 Apply the restored theme before normal review interaction begins, and verify a theme change does not reset loaded decisions, playback position, export controls, or current transcript selection.

## 3. Verification

- [x] 3.1 Add focused automated coverage for theme-value validation and initialization where the existing browser-page test setup supports it, and verify the relevant test command passes.
- [ ] 3.2 Run the existing review-page regression checks and manually exercise dark-to-light-to-dark switching with loaded review data, verifying normal save and export actions remain available throughout.
