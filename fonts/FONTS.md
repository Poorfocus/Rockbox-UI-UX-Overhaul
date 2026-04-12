# Apple2026 Theme Fonts

The Apple2026 theme uses two font families:

## Inter (included)

The Inter-based `.fnt` files (`13-Inter-SemiBold.fnt`, `16-Inter-SemiBold.fnt`,
`19-Inter-V-padded.fnt`, `20-Inter-SemiBold.fnt`) are converted from the
[Inter typeface](https://rsms.me/inter/) by Rasmus Andersson, released under the
**SIL Open Font License 1.1**. These files are included in the repository.

## SF Pro / SF Compact (included here with notice; can be regenerated locally)

The Apple San Francisco typeface files (`SF Pro Text`, `SF Pro Display`,
`SF Compact Text`, `SF Compact Display`) are proprietary Apple fonts.
This repository currently includes Apple-derived bitmap `.fnt` files for the
Apple2026 research branch under the notice in [`NOTICE`](../NOTICE).
They are not GPL/OFL assets and should be treated as educational / research
artifacts only.

If you need a clean local rebuild from fonts you obtained directly from Apple
(for example from Xcode or the Apple Developer site), regenerate these files:

```
13-SFCompactText-Regular.fnt
14-SFProText-Regular.fnt
15-SFProText-Medium.fnt
15-SFProText-Semibold.fnt
16-SFProText-Medium.fnt
16-SFProText-Regular.fnt
16-SFProText-Semibold.fnt
17-SFProText-Bold.fnt
18-SFProText-Regular.fnt
19-SFProText-Medium.fnt
19-SFProText-Semibold.fnt
20-SFProText-Medium.fnt
20-SFProText-Regular.fnt
22-SFCompactDisplay-Semibold.fnt
22-SFProText-Medium.fnt
22-SFProText-Regular.fnt
25-SFProDisplay-Bold.fnt
28-SFProDisplay-Bold.fnt
35-SFProDisplay-Bold.fnt
```

### Generating the fonts

1. Obtain the Apple SF Pro and SF Compact `.otf` files (available from
   [developer.apple.com/fonts](https://developer.apple.com/fonts/)).
2. Place the OTF files in the `Apple Fonts/` directory at the repo root.
3. Run the font conversion tool:
   ```
   python tools/apple2026_rebuild_fonts_from_otf.py
   ```
4. The generated `.fnt` files will be written into `fonts/`, replacing the
   current Apple2026 bitmaps in your local tree.

### Using an alternative open typeface

If you do not have access to Apple's fonts, Inter (already included) covers most
of the UI. You can also substitute any SIL OFL–licensed sans-serif of your choice
by generating `.fnt` files at the required sizes using `tools/convttf` or
`tools/otf_to_rb12_fnt.py`.
