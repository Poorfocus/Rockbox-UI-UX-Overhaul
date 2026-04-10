# Apple2026 Theme Fonts

The Apple2026 theme uses two font families:

## Inter (included)

The Inter-based `.fnt` files (`13-Inter-SemiBold.fnt`, `16-Inter-SemiBold.fnt`,
`19-Inter-V-padded.fnt`, `20-Inter-SemiBold.fnt`) are converted from the
[Inter typeface](https://rsms.me/inter/) by Rasmus Andersson, released under the
**SIL Open Font License 1.1**. These files are included in the repository.

## SF Pro / SF Compact (not included — must generate locally)

The Apple San Francisco typeface files (`SF Pro Text`, `SF Pro Display`,
`SF Compact Text`, `SF Compact Display`) are **not** included in this repository.
Apple's fonts are proprietary and may only be used in development on Apple platforms.
Redistributing derived bitmap fonts from them is not permitted.

The following `.fnt` files must be generated locally from fonts you have legally
obtained from Apple (e.g. from Xcode or the Apple Developer site):

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
2. Place the OTF files in the `Apple Fonts/` directory at the repo root
   (this directory is gitignored).
3. Run the font conversion tool:
   ```
   python tools/apple2026_rebuild_fonts_from_otf.py
   ```
4. The generated `.fnt` files will be placed in `fonts/`. They are gitignored
   and will not be included in any commit.

### Using an alternative open typeface

If you do not have access to Apple's fonts, Inter (already included) covers most
of the UI. You can also substitute any SIL OFL–licensed sans-serif of your choice
by generating `.fnt` files at the required sizes using `tools/convttf` or
`tools/otf_to_rb12_fnt.py`.
