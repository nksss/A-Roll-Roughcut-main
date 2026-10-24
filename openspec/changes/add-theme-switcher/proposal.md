## Why

审片界面目前只提供深色配色，无法适应明亮环境或个人视觉偏好。提供明确的浅色与深色主题切换可提升长时间审片时的可读性，同时保持用户已选择的界面模式。

## What Changes

- 在审片页面的工具栏新增可访问的主题切换控件，可在浅色和深色主题之间切换。
- 保留现有深色主题作为默认主题，避免改变既有用户的首次使用体验。
- 为浅色主题定义覆盖页面、文本、控件、转录高亮、时间轴和状态颜色的完整配色。
- 将用户的主题选择保存在浏览器本地；后续打开同一审片界面时恢复该选择。

## Capabilities

### New Capabilities

- `theme-preference`: Allow review users to select and retain an accessible light or dark visual theme.

### Modified Capabilities

None.

## Impact

- Affected UI: `koubo-roughcut/scripts/review.html`, including its CSS custom properties, toolbar markup, and client-side state initialization.
- Affected browser storage: one new namespaced `localStorage` preference key.
- No changes to review APIs, export behavior, decision data, or Python processing scripts.
