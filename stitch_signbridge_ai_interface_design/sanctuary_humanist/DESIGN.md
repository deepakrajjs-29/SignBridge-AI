---
name: Sanctuary Humanist
colors:
  surface: '#edfdf7'
  surface-dim: '#ceded7'
  surface-bright: '#edfdf7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#e7f7f1'
  surface-container: '#e1f1eb'
  surface-container-high: '#dcece5'
  surface-container-highest: '#d6e6e0'
  on-surface: '#101e1b'
  on-surface-variant: '#41484a'
  inverse-surface: '#25332f'
  inverse-on-surface: '#e4f4ee'
  outline: '#71787a'
  outline-variant: '#c0c8c9'
  surface-tint: '#3e646c'
  primary: '#00262b'
  on-primary: '#ffffff'
  primary-container: '#123c43'
  on-primary-container: '#7fa6ae'
  inverse-primary: '#a5cdd6'
  secondary: '#4e6072'
  on-secondary: '#ffffff'
  secondary-container: '#cee2f7'
  on-secondary-container: '#526577'
  tertiary: '#002721'
  on-tertiary: '#ffffff'
  tertiary-container: '#003f36'
  on-tertiary-container: '#5baf9e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c1eaf2'
  primary-fixed-dim: '#a5cdd6'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#254c54'
  secondary-fixed: '#d1e5fa'
  secondary-fixed-dim: '#b5c9de'
  on-secondary-fixed: '#091d2d'
  on-secondary-fixed-variant: '#36495a'
  tertiary-fixed: '#9ef2e0'
  tertiary-fixed-dim: '#82d6c4'
  on-tertiary-fixed: '#00201b'
  on-tertiary-fixed-variant: '#005045'
  background: '#edfdf7'
  on-background: '#101e1b'
  surface-variant: '#d6e6e0'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 3.5rem
    fontWeight: '700'
    lineHeight: 4.25rem
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 2.25rem
    fontWeight: '700'
    lineHeight: 2.75rem
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 2rem
    fontWeight: '600'
    lineHeight: 2.5rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.5rem
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: 1.75rem
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.25rem
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.875rem
    fontWeight: '600'
    lineHeight: 1.25rem
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.75rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.6875rem
    fontWeight: '500'
    lineHeight: 0.875rem
    letterSpacing: 0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 3rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes a calm, dignified, and utilitarian space dedicated to Indian Sign Language (ISL) visual translation. Because sign language interpretation relies heavily on visual acuity, spatial reading, and sustained screen observation, the visual environment must never compete with video feeds or real-time spatial indicators.

The aesthetic philosophy centers on warm, grounded minimalism. It balances institutional clarity with compassionate warmth:
- **Tone:** Patient, lucid, dependable, and unobtrusive.
- **Target Audience:** Deaf individuals, hard-of-hearing users, sign-language educators, public service interpreters, and non-signing peers requiring fluid real-time communication.
- **Visual Stance:** Restrained and serene. Surfaces evoke archival paper and studio workspaces rather than synthetic AI novelty. Avoid high-frequency micro-interactions, decorative neon flares, or aggressive dimensional effects. Visual quietness directly serves communication legibility.

## Colors

The palette is anchored in tactile organic neutrals paired with deep mineral tones. Contrast meets and exceeds WCAG AAA standards across textual elements to prevent eye strain during sustained signing sessions.

- **Canvas & Backdrops:** Warm Ivory (`#F5F3ED`) acts as the base canvas, reducing high-frequency optical glare inherent in stark pure-white digital displays.
- **Surfaces & Cards:** Crisp White (`#FFFFFF`) isolates translation viewports, camera viewfinders, and chat transcript streams against the ivory base.
- **Primary Tone:** Deep Teal (`#123C43`) commands primary interaction vectors, floating controls, and focused triggers.
- **Structural Text & Navigation:** Midnight Navy (`#172A3A`) supplies decisive authority for global navigation, top-level headings, and structural markers.
- **Active Feedback & Real-Time Recognition:** Soft Seafoam (`#62B6A5`) denotes active camera inputs, tracking confidence, validated gestures, and translation progress without triggering anxiety.
- **Pacing & Accents:** Muted Amber (`#D9A76C`) serves solely as a secondary status indicator (e.g., low-light warnings, tracking recalibrations, or cultural linguistic tips).
- **Secondary Copy:** Muted Grey-Green (`#667570`) provides legible contextual metadata without fighting the primary text hierarchy.
- **Dividers & Structural Rules:** Soft Bisque Border (`#E2DFD6`) delivers razor-sharp 1px separation without visual noise.

## Typography

Typography is set in **Plus Jakarta Sans**, chosen for its balance of geometric precision and humanist legibility. Wide apertures, distinct letterform counters, and clear tall x-height allow immediate parsing for users reading translated text while concurrently watching sign expressions.

- **Visual Pacing:** Translation outputs prioritize readability at a glance. Real-time captions default to `headline-md` or `body-lg` to guarantee legibility from a 2-meter camera setup distance.
- **Micro-Copy:** System telemetry (e.g., frame rate, tracking stability, hand landmark visibility) utilizes strictly uppercase `label-sm` or `label-md` with slight letter-spacing to avoid colliding with conversational transcripts.
- **Hierarchy Separation:** Headlines use Midnight Navy (`#172A3A`) for resolute clarity, while real-time subtitles and running translations adopt Deep Teal (`#123C43`) for a softer, focused engagement.

## Layout & Spacing

The layout operates on a fluid 12-column grid system built to handle dynamic asymmetrical splits between the camera/avatar viewport and the bidirectional transcript console.

- **Workspace Logic:**
  - **Desktop (1024px+):** Employs a primary dual-pane workspace. The video framing pane retains a 4:3 or 16:9 aspect ratio, anchoring 65% of the viewport width. The translated text transcript occupies the remaining 35%. Section margins stay generous at `3rem` (`margin`) to keep peripheral sightlines uncluttered.
  - **Tablet (768px – 1023px):** Collapses into an 8-column layout. Gaps and gutters scale to `1.25rem`, allowing the sign canvas to dominate the upper screen area while text sits directly below.
  - **Mobile (< 768px):** A single 4-column column flow with `1rem` edge margins (`margin-mobile`). The live translation field overlaps or pins to the lower third with floating controls, maximizing visual space for hands, torso, and facial grammar.
- **Rhythm:** Spacing follows strict multiples of 4px/8px. Component interiors stick strictly to `space-md` (`1rem`) and `space-lg` (`1.5rem`) so interactive tap targets remain comfortably above 48px.

## Elevation & Depth

This system intentionally rejects heavy, multi-stop ambient shadows and glossy skeuomorphism. Depth is achieved purely through planar stacking, tactile surface contrast, and quiet 1px line architecture.

- **Tier 0 (Base Foundation):** Warm Ivory (`#F5F3ED`) solid canvas.
- **Tier 1 (Panels & Card Containers):** Crisp White (`#FFFFFF`) with a clean 1px border of `#E2DFD6`. No drop shadow.
- **Tier 2 (Active Camera Viewports & Overlays):** Crisp White or translucent white (`rgba(255, 255, 255, 0.95)`) framed by `#E2DFD6`, elevated by an ultra-subtle, warm ground shadow: `box-shadow: 0 4px 16px -2px rgba(23, 42, 58, 0.04)`.
- **Tier 3 (Floating HUD & Contextual Toolbars):** Deep Teal (`#123C43`) or solid white elevated with `box-shadow: 0 8px 24px -4px rgba(23, 42, 58, 0.08)`.
- **Active State Highlights:** Active tracking states highlight containers using a direct 1.5px outline of Soft Seafoam (`#62B6A5`) without outer halo blurs.

## Shapes

The shape vocabulary uses restrained, human-scaled geometry. Corners are rounded just enough to feel organic and comfortable, never playful or exaggerated.

- **Standard Elements (Buttons, Inputs, Cards):** Formed with an 8px radius (`roundedness: 2`), ensuring clear silhouette boundaries while softening hard digital edges.
- **Larger Video Shells & Modular Frames:** Use `rounded-lg` (16px) to comfortably cradle camera viewports and complex chat streams.
- **Status Indicators & Action Tags:** Small pills and badges use full circular enclosures to immediately indicate functional chips versus rectangular reading content.

## Components

### Buttons
- **Primary:** Deep Teal (`#123C43`) background, White (`#FFFFFF`) text, 8px border radius, 0px border. Height 44px (touch-first 48px on mobile). On hover: Deepen to Midnight Navy (`#172A3A`).
- **Secondary / Ghost:** Transparent background, 1px border in `#E2DFD6`, Midnight Navy (`#172A3A`) text. On hover: Background `#F5F3ED` with border tone `#667570`.
- **Active Communication Trigger:** Soft Seafoam (`#62B6A5`) background with Midnight Navy (`#172A3A`) text for one-tap action states (e.g., "Start Signing", "Confirm Interpretation").

### Cards & Viewport Shells
- Built with a `#FFFFFF` fill, 8px corner radius, and an enclosing 1px border (`#E2DFD6`).
- Video translation frames feature unobtrusive overlay nodes at the corners to verify hand-mesh landmarks without obstructing the user's face.

### Chips & Badges
- **Status Chips:** Height 28px, rounded pill format. Soft Seafoam tint (`rgba(98, 182, 165, 0.15)`) with Deep Teal text indicates "Sign Detected".
- **Dialect / Language Chips:** Neutral White background with a 1px `#E2DFD6` border and Muted Grey-Green (`#667570`) label to specify regional ISL variations (e.g., "ISL — Northern Syntax").

### Input Fields & Search Bars
- Background `#FFFFFF`, 1px solid `#E2DFD6` border, 8px corner radius. Placeholder text rendered in `#667570`.
- On focus: 1.5px solid Deep Teal (`#123C43`) outline with zero glow rings.

### Checkboxes & Radio Controls
- Base: 20px box, 4px border radius for checkboxes, full circle for radios. 1.5px border `#667570`.
- Selected: Deep Teal fill with white central icon check or center dot.

### Real-Time Translation Stream
- Visualized as an uninterrupted conversational river. Inbound signed translations are framed in pure white cards with an indented left accent border (2px solid Soft Seafoam `#62B6A5`). Text-to-sign prompts sit slightly offset with a warm ivory tone and Midnight Navy typography.