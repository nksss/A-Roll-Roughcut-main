## Purpose

让口播审片用户在不影响现有剪辑、播放或导出工作流的前提下，选择清晰可读的浅色或深色界面主题，并在后续访问时保留偏好。

## ADDED Requirements

### Requirement: Review interface provides an explicit theme switcher
The review interface SHALL expose a toolbar control that lets users switch between light and dark themes. The control MUST convey its current theme and its action or state to assistive technologies.

#### Scenario: User switches from the default dark theme to the light theme
- **WHEN** a user activates the theme control while the dark theme is active
- **THEN** the review interface immediately renders using the light theme and the control reflects the light theme as active

#### Scenario: User switches from the light theme to the dark theme
- **WHEN** a user activates the theme control while the light theme is active
- **THEN** the review interface immediately renders using the dark theme and the control reflects the dark theme as active

### Requirement: Each supported theme covers the complete review workspace
The review interface SHALL apply the selected theme consistently to page surfaces, panels, text, borders, interactive controls, transcript selection and playback highlights, timeline surfaces, and status colors. Theme changes MUST NOT alter review decisions, playback state, export options, or other review data.

#### Scenario: User changes theme during an active review session
- **WHEN** a user changes the theme after loading review data or making review selections
- **THEN** the interface changes visual colors while preserving the current review data, selections, and available actions

### Requirement: Theme selection persists locally
The review interface SHALL use dark theme when no valid saved preference exists. After a user selects a supported theme, the interface MUST restore that selection on a later visit in the same browser profile.

#### Scenario: First visit without a saved preference
- **WHEN** the review interface opens and no saved theme preference is available
- **THEN** it renders in the dark theme

#### Scenario: Returning visit with a saved light preference
- **WHEN** the review interface opens in a browser profile that previously saved the light theme
- **THEN** it renders in the light theme before the user changes the control
