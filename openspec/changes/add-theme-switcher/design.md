## Context

The review UI is a self-contained HTML page with its visual rules defined in an inline stylesheet. Existing dark-theme colors are split between CSS custom properties and direct color literals. The page already stores browser-local interface preferences for playback rate and transcript-pane width. See `proposal.md` for motivation and `specs/theme-preference/spec.md` for required behavior.

## Goals / Non-Goals

**Goals:**

- Add a compact toolbar control that makes the active theme and its affordance clear to keyboard and assistive-technology users.
- Keep the current dark appearance as the no-preference fallback.
- Switch all visible review surfaces through a single theme state without disturbing in-memory review state.
- Restore the most recently selected valid theme from the browser's local storage.

**Non-Goals:**

- Following the operating-system color-scheme automatically.
- Adding more than light and dark themes, theme customization, or a server-synchronized preference.
- Changing review, export, or media behavior.

## Decisions

### Use a document-level theme attribute and semantic CSS tokens

Apply the selected mode as a data attribute on the root document element and define dark and light token values under theme-specific selectors. Replace color literals used by interactive and structural review surfaces with these tokens, while retaining deliberate fixed media black where appropriate.

This localizes color selection in CSS, avoids per-component JavaScript style changes, and ensures one state change updates the entire page. A class on `body` was considered, but a root-level attribute better covers root and body background painting and keeps the scope explicit.

### Use an explicit two-state toolbar button

Add one button in the existing header toolbar that toggles between the two modes. Its visible label, title, and ARIA state will identify the active mode or resulting action without relying on color or an icon alone.

A native select was considered, but a two-state action is faster for the only two supported modes and fits the existing compact toolbar controls.

### Persist only validated theme values in local storage

Store the selected mode under a new `koubo-review-*` key. During startup, read the key before applying the initial visual mode; missing, inaccessible, or invalid values fall back to dark. Storage reads and writes follow the page's current guarded `localStorage` usage so private-mode or quota failures do not block review.

Using a server-side preference was considered, but the review page has no account model and this display preference has no need to cross devices.

## Risks / Trade-offs

- [Hard-coded dark colors remain after tokenization] → Audit every page surface and stateful control in the stylesheet, including canvas drawing and the marquee overlay, before accepting the implementation.
- [Light theme reduces the visibility of selection, warning, or focus states] → Define distinct semantic tokens for text, muted text, borders, accent, selection, keep, and drop states, then verify both themes through key review interactions.
- [Stored values become stale or corrupted] → Accept only the two supported values and use the dark default for all other values.
- [A theme flashes during page initialization] → Apply the restored attribute during initial startup before the page is made interactive; a small inline document-start initializer is acceptable if required to avoid the flash.

## Migration Plan

1. Deploy the UI change with dark as the fallback for every absent or invalid preference.
2. Existing browser profiles receive the dark fallback until the user makes a choice; no data migration is required.
3. To roll back, remove the control and theme overrides; the unused local storage key is harmless and existing review data is unaffected.
