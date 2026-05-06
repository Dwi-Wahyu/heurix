---
name: Executive Maroon
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#5a413d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#8e706c'
  outline-variant: '#e2bfb9'
  surface-tint: '#b22b1d'
  primary: '#570000'
  on-primary: '#ffffff'
  primary-container: '#800000'
  on-primary-container: '#ff8371'
  inverse-primary: '#ffb4a8'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fd'
  on-secondary-container: '#57657b'
  tertiary: '#272726'
  on-tertiary: '#ffffff'
  tertiary-container: '#3d3d3b'
  on-tertiary-container: '#a9a7a5'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad4'
  primary-fixed-dim: '#ffb4a8'
  on-primary-fixed: '#410000'
  on-primary-fixed-variant: '#8f0f07'
  secondary-fixed: '#d5e3fd'
  secondary-fixed-dim: '#b9c7e0'
  on-secondary-fixed: '#0d1c2f'
  on-secondary-fixed-variant: '#3a485c'
  tertiary-fixed: '#e5e2df'
  tertiary-fixed-dim: '#c8c6c3'
  on-tertiary-fixed: '#1c1c1a'
  on-tertiary-fixed-variant: '#474745'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-bold:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 24px
  margin: 32px
---

## Brand & Style

This design system is engineered for high-stakes professional environments. It targets mid-to-senior level professionals preparing for rigorous interviews, demanding a visual language that communicates precision, authority, and reliability. The aesthetic is rooted in **Corporate Modernism**, drawing inspiration from high-end executive dashboards and tactical assessment tools.

The user experience should feel focused and intentional. By utilizing deep, saturated brand tones against a canvas of sophisticated neutrals, the interface establishes a "command center" atmosphere. Large amounts of white space, combined with crisp typography and subtle depth, ensure that the gravity of the simulation is felt without overwhelming the user with unnecessary visual noise.

## Colors

The palette is anchored by a deep **Executive Maroon**, a color that signals tradition, power, and seriousness. This is balanced by a suite of slate grays and off-whites to prevent the UI from feeling overly aggressive or dated.

- **Primary:** #800000 (Maroon). Used for key actions, branding, and status indicators of high importance.
- **Secondary:** #334155 (Slate Blue-Gray). Used for secondary navigation, headings, and high-contrast text.
- **Tertiary/Surface:** #F8F5F2 (Bone White). A warm off-white used for the main background to reduce eye strain compared to pure white.
- **Neutral:** #64748B (Muted Slate). Used for supporting text, borders, and disabled states.
- **Semantic:** Success is indicated by a desaturated forest green; warnings by a burnt orange to maintain the "serious" tone.

## Typography

This design system utilizes **Plus Jakarta Sans** exclusively to bridge the gap between modern tech and traditional professionalism. The font's wide stance and clean terminals provide excellent legibility during timed assessments.

Headlines should be set with tight letter spacing and heavier weights to project authority. Body text maintains a generous line height to ensure readability of complex interview questions and feedback reports. Labels utilize uppercase styling with increased tracking to differentiate "data" from "narrative" content, echoing military or corporate documentation styles.

## Layout & Spacing

The design system employs a **Fixed Grid** philosophy for desktop (1280px max-width) and a fluid 4-column system for mobile. A strict 4px baseline grid ensures vertical rhythm across all components.

Layouts are designed with "Air and Focus." Margins are generous (32px+) to isolate content sections, mimicking the layout of a premium physical report. Interaction zones are clearly delineated with margins to prevent accidental clicks during high-pressure simulation tasks. Use "MD" (16px) for internal component padding and "XL" (40px) for separating major functional blocks.

## Elevation & Depth

To maintain a serious and modern aesthetic, depth is communicated through **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows.

- **Level 0 (Floor):** The Tertiary background (#F8F5F2).
- **Level 1 (Cards):** Pure white (#FFFFFF) surfaces with a subtle 1px border (#E2E8F0).
- **Level 2 (Active/Hover):** A very soft, diffused shadow (0px 4px 20px rgba(51, 65, 85, 0.08)) is used only for active elements or "floating" modals to indicate they are above the primary workspace.

This "Flat-Plus" approach ensures the interface feels like a sophisticated tool rather than a toy.

## Shapes

The shape language is controlled and "Soft-Industrial." Standard UI elements like buttons and input fields use a **10px (0.625rem) radius**. This provides a modern, approachable feel while maintaining enough structural rigidity to appear professional.

Larger containers, such as dashboard cards or video preview windows, can scale up to **16px (1rem)** for a more "encapsulated" look. Icons should follow a consistent 2px stroke width with slightly rounded terminals to match the typography.

## Components

### Buttons
- **Primary:** Solid Executive Maroon with white text. High-contrast, no gradient. 
- **Secondary:** Transparent background with a 2px Maroon border.
- **Ghost:** Slate Gray text, no border; used for low-priority actions like "Cancel" or "Skip."

### Input Fields
- Understated styling with a light gray fill (#F1F5F9) and a bottom-only border that turns Maroon on focus. This mimics "filling out a form" in a high-end corporate setting.

### Cards & Containers
- All cards should have a white background and 10px rounded corners. Use a 1px border (#E2E8F0) instead of shadows to define boundaries.

### Progress & Assessment Indicators
- Use a "Step" indicator for multi-part interviews. Completed steps are solid Maroon; current steps are Maroon outlines; future steps are Slate Gray. 

### Specialized Components
- **Timer/Countdown:** Displayed in a semi-bold Slate Gray with a Maroon "warning" pulse when less than 60 seconds remain.
- **Speech Waveform:** A custom visualization for audio-based simulations, using varying shades of Maroon to represent voice activity.