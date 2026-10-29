---
name: Yael
description: Minimalist Corporate Document Intelligence Platform
colors:
  primary: "#ffffff"
  primary-hover: "#f4f4f5"
  secondary: "#27272a"
  status-healthy: "#10b981"
  status-warning: "#f59e0b"
  status-danger: "#ef4444"
  bg-canvas: "#09090b"
  bg-surface: "#18181b"
  bg-elevated: "#27272a"
  border-subtle: "#18181b"
  border-default: "#27272a"
  text-primary: "#fafafa"
  text-secondary: "#a1a1aa"
  text-muted: "#71717a"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.5
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1.5
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
    fontSize: "0.6875rem"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.02em"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  xl: "12px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.bg-canvas}"
    rounded: "{rounded.md}"
    padding: "6px 12px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
    padding: "4px 8px"
  card-citation:
    backgroundColor: "{colors.bg-surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "10px"
  badge-status:
    backgroundColor: "transparent"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.full}"
    padding: "2px 6px"
---

# Design System: Yael

## Overview

**Creative North Star: "The Executive Dossier"**

Yael's interface is an uncompromising corporate minimalist workspace designed for executives, analysts, and enterprise teams. It eliminates all decorative clutter, visual noise, unnecessary badges, and colorful gradients in favor of structural clarity, generous breathing room, and immaculate typography.

Information density is strictly calibrated to task necessity. Non-actionable telemetry (AI model branding, database infrastructure labels, internal thresholds) is removed from persistent viewports. Provenance is preserved as a sleek, unobtrusive record that users can audit on demand with high contrast and zero friction.

**Key Characteristics:**
- Deep Zinc canvas (`#09090b`) with hairline architectural dividers (`#27272a`).
- Maximum text contrast: pure `#fafafa` headings (21:1 contrast ratio) and `#a1a1aa` secondary copy (7.5:1 ratio, exceeding WCAG AAA).
- Complete elimination of extraneous chrome badges and colorful clutter.
- Compact, quiet citation chips showing only document title, page number, and verified excerpts.
- Monolith high-contrast primary controls (solid white on dark zinc).

## Colors

The palette is built on neutral zinc values with strict contrast thresholds and monochromatic discipline.

### Primary
- **Monolith White** (`#ffffff` / `#fafafa`): Primary action buttons, dominant titles, and active input icons (21:1 contrast ratio).
- **Subtle Surface Hover** (`#f4f4f5`): Hover state for white primary interactive elements.

### Secondary
- **Deep Zinc Surface** (`#18181b`): Modal containers, dropdown menus, and subtle message query blocks.

### Neutral
- **Obsidian Zinc Canvas** (`#09090b`): The foundational dark background canvas.
- **Hairline Border** (`#27272a`): 1px structural dividing lines.
- **Pure Text** (`#fafafa`): High-contrast reading typography.
- **Muted Slate** (`#a1a1aa`): Secondary body text, timestamps, and subtle counts.
- **Quiet Caption** (`#71717a`): Tertiary metadata, placeholders, and keyboard shortcut legends.

### Semantic Accents (Restrained)
- **Status Emerald** (`#10b981`): Discrete system healthy indicator dot.
- **Warning Amber** (`#f59e0b`): Contextual insufficient certainty notice.
- **Danger Red** (`#ef4444`): Irreversible document deletion confirmations.

### Named Rules
**The Essential Information Doctrine.** If an interface element merely documents an internal technology name without affecting user action, it is deleted from the screen.

**The High-Contrast Floor.** All body and interaction text must achieve at least 7.0:1 contrast against its immediate surface.

## Typography

**Display Font:** Inter, system-ui, -apple-system, sans-serif
**Body Font:** Inter, system-ui, -apple-system, sans-serif
**Label/Mono Font:** ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace

**Character:** Understated, neutral Swiss-inspired typographic discipline with tight kerning for titles and crisp tabular monospace for numerical metrics and page indices.

### Hierarchy
- **Display** (Semibold, 1.125rem / 18px, line-height 1.25, letter-spacing -0.025em): Modal headers and empty state greeting.
- **Headline** (Semibold, 0.875rem / 14px, line-height 1.5, letter-spacing -0.01em): Brand logo and primary view titles.
- **Title** (Medium, 0.8125rem / 13px, line-height 1.5): Document titles, sidebar categories, and prompt pills.
- **Body** (Regular, 0.8125rem / 13px, line-height 1.65): Verified answers and source snippets.
- **Label** (Medium / Monospace, 0.6875rem / 11px, letter-spacing 0.02em): Page references ("Pág. 4"), percentages, and document counts.

## Layout

- **Top Navigation Bar:** Compact 56px (`h-14`) bar with 1px border (`border-b border-zinc-800`), clean brand mark, and quiet status heartbeat.
- **Document Sidebar:** 288px (`w-72`) column with instant search, clean document listing, and a compact upload button.
- **Main Reading Stream:** Clean vertical thread centered in `max-w-3xl` (~75ch) measure, keeping line lengths optimal for reading.

## Elevation & Depth

Zero drop shadows on rested elements. Surfaces rely entirely on 1px hairline borders (`#27272a`) and subtle background shifts (`#09090b` vs `#18181b`).

## Shapes

- **Radius:** Subtle, tight corners (6px `rounded-md` for buttons and inputs, 8px `rounded-lg` for citation containers and modals).
- **Borders:** Consistent 1px neutral stroke (`#27272a`).

## Components

### Buttons
- **Primary:** Solid white `#ffffff`, text `#09090b`, 6px radius, hover to `#f4f4f5`.
- **Secondary / Ghost:** Transparent background, text `#a1a1aa`, hover to `#18181b` and `#fafafa`.

### Citation Chips
- **Container:** Border `#27272a`, background `#18181b`/60.
- **Content:** Document name truncate, monospace page tag, and percentage match.
- **Expanded:** Deep `#09090b` inset container with clean whitespace-preserved text.

## Do's and Don'ts

### Do:
- **Do** preserve the deep zinc palette (`#09090b`) with white (`#fafafa`) text for maximum contrast.
- **Do** keep persistent chrome free of unnecessary badges and tech jargon.
- **Do** present citations as compact, expandable references.

### Don't:
- **Don't** add decorative gradients, colored glows, or heavy drop shadows.
- **Don't** clutter the header with redundant model or infrastructure names.
- **Don't** use low-contrast text below WCAG AAA (7:1).
