#!/usr/bin/env python3
"""Shared Apple2026 palette tokens for generators and audits.

The Apple2026 light-shell reset uses stock neutral white as the single source of
truth. Generator scripts should import from here instead of carrying local shell
constants that can drift out of sync.
"""

SHELL_BG = (255, 255, 255)
SHELL_BG_HEX = "FFFFFF"
SHELL_BG_HEX_LOWER = "ffffff"

TEXT_PRIMARY = (0, 0, 0)
TEXT_SECONDARY = (110, 110, 115)
TEXT_TERTIARY = (60, 60, 67)
ACCENT = (255, 45, 85)

OPAQUE_SEPARATOR = (198, 198, 200)
SUBTLE_SEPARATOR = (229, 229, 234)
GROUPED_FILL = (242, 242, 247)
PROGRESS_TRACK = (199, 199, 204)

QS_WHEEL_FILL = (242, 242, 247)
QS_WHEEL_OUTLINE = (214, 214, 219)
