---
name: Jalnetra Design System
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45474c'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#545f73'
  primary: '#091426'
  on-primary: '#ffffff'
  primary-container: '#1e293b'
  on-primary-container: '#8590a6'
  inverse-primary: '#bcc7de'
  secondary: '#006591'
  on-secondary: '#ffffff'
  secondary-container: '#39b8fd'
  on-secondary-container: '#004666'
  tertiary: '#1e1200'
  on-tertiary: '#ffffff'
  tertiary-container: '#35260c'
  on-tertiary-container: '#a38c6a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e3fb'
  primary-fixed-dim: '#bcc7de'
  on-primary-fixed: '#111c2d'
  on-primary-fixed-variant: '#3c475a'
  secondary-fixed: '#c9e6ff'
  secondary-fixed-dim: '#89ceff'
  on-secondary-fixed: '#001e2f'
  on-secondary-fixed-variant: '#004c6e'
  tertiary-fixed: '#fadfb8'
  tertiary-fixed-dim: '#ddc39d'
  on-tertiary-fixed: '#271902'
  on-tertiary-fixed-variant: '#564427'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: monospace
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-margin-mobile: 16px
  container-margin-desktop: 32px
  gutter: 16px
  stack-gap: 12px
  grid-columns-desktop: '12'
  grid-columns-mobile: '4'
---

## Brand & Style

The design system is engineered for high-stakes environmental monitoring and disaster response. It adopts a **Modern-Corporate** aesthetic with a heavy focus on **Utility and Precision**. The primary goal is to project absolute authority and calm during crises.

The visual language prioritizes information density and clarity over decorative elements. It utilizes a structured, systematic approach inspired by aviation and industrial control systems—where cognitive load must be minimized. The style is characterized by flat surfaces, crisp edges, and a restrained use of elevation to ensure that data visualization and status indicators remain the primary focus of the user's attention.

## Colors

The palette is anchored by **Deep Navy (#1E293B)**, representing the institutional stability of the Indian government. This primary color is used for navigation, headers, and primary actions to establish a clear hierarchy.

A semantic color system is strictly enforced for disaster levels:
- **Normal (Emerald):** Systemic stability.
- **Awareness (Sky Blue):** Informational updates without immediate threat.
- **Watch (Amber):** Heightened monitoring required.
- **Warning (Orange):** Imminent localized threat.
- **Critical (Crimson):** Immediate evacuation and life-safety protocols.

Backgrounds utilize **Off-white (#F8FAFC)** to reduce eye strain during long monitoring shifts, while surfaces use pure **White (#FFFFFF)** to create subtle contrast for data cards and input modules.

## Typography

This design system utilizes **Inter** for all interfaces due to its exceptional legibility at small sizes and high x-height, which is critical for GIS data and field operations. 

- **Headlines:** Use semi-bold weights with tight tracking to appear authoritative and urgent.
- **Body:** Standardized at 16px for desktop and mobile to ensure readability under high-stress or low-light conditions.
- **Labels:** Small labels use an uppercase treatment with increased letter spacing to differentiate metadata from body content.
- **Data Display:** For coordinates, timestamps, and water levels, a monospaced fall-back is used to ensure numerical alignment in tables and dashboards.

## Layout & Spacing

The layout philosophy is based on a **strict 4px baseline grid** to achieve a dense, functional interface. 

- **Command Mode (Desktop):** A 12-column fluid grid. Sidebars for telemetry and alerts are fixed at 320px, while the central map area expands to fill the viewport.
- **Responder Mode (Tablet/Mobile):** A single-column stack with 16px margins. Elements are sized for "gloved-hand" touch targets (min 44px height) while maintaining high information density.
- **Citizen Mode (Mobile):** High-contrast vertical layouts with oversized alert banners.

Spacing between related data points is kept tight (8px-12px) to allow for "at-a-glance" monitoring of multiple sensors simultaneously.

## Elevation & Depth

To maintain a sense of precision, this design system avoids heavy shadows. Depth is communicated through **Tonal Layering** and **Low-Contrast Outlines**.

1.  **Level 0 (Background):** #F8FAFC. The canvas for all content.
2.  **Level 1 (Cards/Modules):** #FFFFFF with a 1px border (#E2E8F0). This is the default state for data containers.
3.  **Level 2 (Overlays/Modals):** A very soft, diffused shadow (0px 4px 6px rgba(30, 41, 59, 0.05)) is used only for elements that temporarily float over the map or primary UI, such as emergency broadcast pop-ups.
4.  **Active State:** Elements being interacted with use a 2px stroke in the primary Navy color rather than a shadow.

## Shapes

The shape language is **Soft-Geometric**. A base roundedness of **4px (0.25rem)** is applied to buttons, input fields, and containers. This slight rounding provides a modern feel without sacrificing the "serious" and "structured" institutional look required for a government service.

- **Status Badges:** Use a slightly higher radius (8px) to distinguish them from functional buttons.
- **Emergency Buttons:** Are kept strictly rectangular or with the base 4px radius to maximize the clickable surface area and maintain a "tool-like" appearance.

## Components

- **Buttons:** Primary buttons use the Deep Navy background with white text. Secondary buttons use a 1px Navy border. Success/Danger actions use the respective status colors.
- **Status Chips:** Critical components. They must feature a leading icon (e.g., a wave, a warning triangle) followed by bold text. They utilize high-saturation backgrounds for immediate visibility.
- **Data Cards:** White background, 1px #E2E8F0 border. Headers within cards should have a subtle #F1F5F9 background tint to separate the title from the data.
- **Input Fields:** Squared-off corners (4px), clear 1px borders. Focused states must use a high-contrast 2px #0EA5E9 (Sky Blue) border to ensure users know exactly where they are typing.
- **Alert Banners:** Full-width components that sit at the top of the viewport. They use the Status colors and include a "Time Elapsed" ticker to show data freshness.
- **Telemetry Lists:** Compact rows with a monospaced font for numerical values, separated by subtle horizontal dividers.