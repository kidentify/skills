---
name: neimo-design-system
description: >-
  Neimo's visual design system for HTML deliverables — client blueprints, data
  stories, presentation decks, blog diagrams, and marketing mocks. Defines the
  shared design DNA (grain, typography, color semantics, components) and five
  distinct asset modes with their tokens, layouts, and component libraries. Use
  when building any visual HTML asset, creating charts or diagrams, designing
  client-facing documents, or when the user mentions "same style as the blueprint", "Neimo look", "data story", "blog
  graphic", or any visual deliverable.
---

# Neimo Visual Design System

Five asset modes, one design DNA. Pick the mode, apply the tokens, build.

## Quick — Which Mode?

| Building this? | Use this mode |
|----------------|---------------|
| Client deliverable (blueprint, one-pager, integration guide) | **Client Blueprint** |
| Scroll narrative with charts and data (market story, impact report) | **Data Story** |
| Full-bleed slide deck for sharing/presenting | **Presentation Deck** |
| Single embeddable graphic (flow, decision tree, timeline, bar chart) | **Blog Diagram** |
| Website page mock (homepage, product page, landing page) | **Marketing Mock** |

Need a PDF? After building the HTML, follow the `html-slide-to-pdf` skill for
Playwright export, QA checklist, and page assembly.

---

## Shared DNA (applies to ALL modes)

These patterns are present across every Neimo visual asset and form the
signature look. Apply them regardless of which mode you pick. Keep the brand
expression tight: lead with Neimo purple, use indigo and cyan as secondary
accents, and reserve green/red for explicit status states.

### Film Grain Overlay

```css
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.016;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 256px 256px;
}
```

Opacity range: 0.015–0.018. Disable in print (`display: none !important`).

### Color Semantics

These meanings are consistent across all modes — only the specific hex values
shift between palettes:

| Role | Meaning | Light default | Dark default |
|------|---------|---------------|-------------|
| **Purple** | Neimo brand, primary accent | `#7026F9` | `#A57BF5` |
| **Indigo** | Structural emphasis, product depth | `#4264D1` | `#8EA4FF` |
| **Cyan** | Secondary highlight, assistant glow | `#6CE2FF` | `#B8F1FF` |
| **Violet/Lilac** | Soft emphasis, prompt surfaces | `#715DEC` | `#AF7EFF` |
| **Green** | Success, approval | `#30A46C` | `#4ADE80` |
| **Red** | Danger, prohibition | `#E5484D` | `#FF6F71` |

### Typography Rules

| Element | Treatment |
|---------|-----------|
| Headings | Tight tracking (`letter-spacing: -0.03em`), weight 700–900 |
| Body | `line-height: 1.55`, weight 400 |
| Section labels | Monospace, `0.52–0.65rem`, uppercase, `letter-spacing: 0.2–0.25em` |
| Stats/numbers | Monospace, large, weight 700, accent color |
| Editorial accent | Serif italic inside `<em>` in headings — one or two key words |
| API/code labels | Monospace, small, uppercase or code-case |

### 3px Accent Bar

Every section header and card top uses a 3px color-coded strip:

```css
.accent-bar {
  width: 48px;
  height: 3px;
  margin-bottom: 24px;
}
.accent-bar--purple { background: var(--purple); }
.accent-bar--teal   { background: var(--teal); }
.accent-bar--coral  { background: var(--coral); }
```

Cards use `::before` for the full-width top strip:

```css
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
}
```

### Soft Radial Backgrounds

Never hard linear gradients on page backgrounds. Use elliptical radial blobs:

```css
background:
  radial-gradient(ellipse 55% 50% at 15% 10%, rgba(112, 38, 249, 0.03), transparent),
  radial-gradient(ellipse 45% 45% at 85% 85%, rgba(108, 226, 255, 0.03), transparent),
  var(--void);
```

### Print CSS (required in every file)

```css
@media print {
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  body { overflow: visible !important; }
  body::after { display: none !important; }
  .anim, .anim-scale { opacity: 1 !important; transform: none !important; }
}
```

### Icons

**Google Material Symbols Rounded** (filled). Never emojis. Never Font Awesome.

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap">
```

```css
.material-symbols-rounded {
  font-variation-settings: 'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24;
}
```

Icon containers: 36px rounded squares with glow background and matching color
border at 12% opacity.

### Neimo Wordmark

The canonical Neimo wordmark is the **`neimo` lowercase logotype with the
trailing accent dot**, shipped with this skill at `assets/neimo-logo.svg`.
The SVG uses `fill="currentColor"` so it inherits whatever color CSS sets on
it — defaults to `--purple`, recolors automatically in dark variants.

**Primary form — inline SVG.** Paste the contents directly into the HTML so
deliverables stay single-file. This is what every Neimo-shipped HTML asset
should use.

```html
<svg class="neimo-wordmark" viewBox="0 0 66 17" height="22"
     xmlns="http://www.w3.org/2000/svg" fill="none">
  <path fill="currentColor" d="M1.39258 16.8345C0.572754 16.8345 0 16.3066 0 15.3633V5.88477C0 5.02002 0.505371 4.46973 1.33643 4.46973C2.15625 4.46973 2.71777 5.02002 2.71777 5.88477V6.71582H2.77393C3.41406 5.30078 4.64941 4.48096 6.47998 4.48096C9.10791 4.48096 10.6016 6.16553 10.6016 8.91699V15.3633C10.6016 16.3066 10.0288 16.8345 9.20898 16.8345C8.38916 16.8345 7.80518 16.3066 7.80518 15.3633V9.47852C7.80518 7.79395 7.01904 6.85059 5.42432 6.85059C3.81836 6.85059 2.79639 8.00732 2.79639 9.71436V15.3633C2.79639 16.3066 2.2124 16.8345 1.39258 16.8345ZM18.1372 16.8457C14.4985 16.8457 12.3535 14.5659 12.3535 10.7026C12.3535 6.90674 14.5435 4.4585 17.98 4.4585C21.2368 4.4585 23.4604 6.77197 23.4604 10.0063C23.4604 10.8374 22.9888 11.3315 22.1577 11.3315H15.1387V11.4214C15.1387 13.4092 16.2954 14.6895 18.1147 14.6895C19.3726 14.6895 20.1924 14.2515 21.0908 13.106C21.3828 12.7803 21.6411 12.6567 22.0342 12.6567C22.6631 12.6567 23.1572 13.061 23.1572 13.7349C23.1572 13.9482 23.0898 14.1953 22.9663 14.4424C22.1802 15.9585 20.4058 16.8457 18.1372 16.8457ZM15.1611 9.48975H20.7202C20.6641 7.76025 19.5635 6.62598 17.9912 6.62598C16.4189 6.62598 15.2734 7.78271 15.1611 9.48975ZM26.7285 3.03223C25.8638 3.03223 25.1787 2.3584 25.1787 1.51611C25.1787 0.662598 25.8638 0 26.7285 0C27.6045 0 28.2896 0.662598 28.2896 1.51611C28.2896 2.3584 27.6045 3.03223 26.7285 3.03223ZM26.7285 16.8345C25.875 16.8345 25.3359 16.2729 25.3359 15.3633V5.94092C25.3359 5.04248 25.875 4.46973 26.7285 4.46973C27.582 4.46973 28.1323 5.04248 28.1323 5.95215V15.3633C28.1323 16.2729 27.582 16.8345 26.7285 16.8345ZM31.8721 16.8345C31.0298 16.8345 30.4795 16.2954 30.4795 15.3633V5.896C30.4795 4.98633 31.0298 4.46973 31.8159 4.46973C32.6021 4.46973 33.1636 4.98633 33.1636 5.896V6.77197H33.2197C33.7363 5.39062 34.9941 4.48096 36.6113 4.48096C38.2959 4.48096 39.4976 5.3457 39.9355 6.87305H40.0029C40.5757 5.40186 41.9907 4.48096 43.709 4.48096C46.0562 4.48096 47.5947 6.06445 47.5947 8.44531V15.3633C47.5947 16.2954 47.0332 16.8345 46.2021 16.8345C45.3599 16.8345 44.7983 16.2954 44.7983 15.3633V9.13037C44.7983 7.67041 44.0347 6.83936 42.6646 6.83936C41.3169 6.83936 40.396 7.82764 40.396 9.25391V15.3633C40.396 16.2954 39.8682 16.8345 39.0371 16.8345C38.1948 16.8345 37.6782 16.2954 37.6782 15.3633V8.98438C37.6782 7.65918 36.8696 6.83936 35.5669 6.83936C34.2192 6.83936 33.2759 7.88379 33.2759 9.32129V15.3633C33.2759 16.2954 32.7031 16.8345 31.8721 16.8345ZM55.1079 16.8457C51.6152 16.8457 49.3467 14.521 49.3467 10.6577C49.3467 6.81689 51.6377 4.4585 55.1079 4.4585C58.5781 4.4585 60.8691 6.80566 60.8691 10.6577C60.8691 14.521 58.6006 16.8457 55.1079 16.8457ZM55.1079 14.6333C56.8823 14.6333 58.0278 13.1958 58.0278 10.6577C58.0278 8.13086 56.8823 6.68213 55.1079 6.68213C53.3447 6.68213 52.188 8.13086 52.188 10.6577C52.188 13.1958 53.3335 14.6333 55.1079 14.6333ZM64.1709 16.7334C63.2612 16.7334 62.5537 16.0259 62.5537 15.1162C62.5537 14.2178 63.2612 13.499 64.1709 13.499C65.0693 13.499 65.7769 14.2178 65.7769 15.1162C65.7769 16.0259 65.0693 16.7334 64.1709 16.7334Z"/>
</svg>
```

```css
.neimo-wordmark {
  display: inline-block;
  color: var(--purple);
  vertical-align: middle;
}

/* Size variants — set height, width auto-scales from viewBox 66×17 (~3.88:1).
   --small is sized to match cap-height of adjacent uppercase mono text in
   credit contexts. Larger sizes for headers and hero use. */
.neimo-wordmark--small  { height: 11px; }
.neimo-wordmark--inline { height: 18px; }
.neimo-wordmark--large  { height: 28px; }
.neimo-wordmark--hero   { height: 40px; }
```

The SVG uses `fill="currentColor"`, so changing `color:` recolors the mark.
That's how it adapts to dark variants (color stays `--purple`, the resolved
hex differs between light and dark token sets) and to the `:hover` states on
chips/headers.

**Alternative form — external file reference.** When the deliverable is in
a folder structure rather than a single file (e.g. a multi-page site mock),
reference the SVG file directly instead of inlining:

```html
<img class="neimo-wordmark" src="assets/neimo-logo.svg" alt="neimo">
```

Note: `<img>` doesn't inherit `currentColor`, so for color variants either
ship pre-tinted SVG files (`neimo-logo-purple.svg`, `neimo-logo-white.svg`)
or stick with inline SVG.

**Fallback form — type-only wordmark.** If the SVG isn't available (legacy
environment, plain-text export, fragments where SVG inflates token count
unacceptably), the fallback is the editorial-accent treatment: Source Serif
4 italic in `--purple`, the same convention used in headings.

```html
<span class="neimo-wordmark-text">neimo</span>
```

```css
.neimo-wordmark-text {
  font-family: 'Source Serif 4', serif;
  font-style: italic;
  font-weight: 700;
  color: var(--purple);
  letter-spacing: -0.01em;
}
```

**Presentation Deck mode** uses Crimson Pro italic instead of Source Serif 4
for the type-only fallback. The SVG primary form is unchanged.

### Top-of-Page Header

Pair with the Powered-by footer. The header is a **quiet signature**, not a
hero element — small wordmark in the top-left, nothing else by default.
Anything that competes with the hero defeats the purpose.

```html
<header class="neimo-header">
  <a class="neimo-header-mark" href="https://neimo.ai" target="_blank" rel="noopener" aria-label="neimo">
    <!-- Inline the Neimo Wordmark SVG from the section above.
         Use the --inline size class (height: 18px) for headers — small. -->
    <svg class="neimo-wordmark neimo-wordmark--inline" viewBox="0 0 66 17"
         xmlns="http://www.w3.org/2000/svg" fill="none">
      <path fill="currentColor" d="M1.39258 16.8345C…"/>  <!-- full path from Wordmark section -->
    </svg>
  </a>
</header>
```

```css
.neimo-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 22px 64px 0;
  max-width: 1080px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}
.neimo-header-mark {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  color: var(--muted);          /* dimmed — not full --purple */
  transition: color 0.2s;
}
.neimo-header-mark:hover { color: var(--purple); }

@media (max-width: 700px) {
  .neimo-header { padding: 18px 24px 0; }
}
```

**Optional — header with tagline.** Use only when there's space and the
header is genuinely useful navigation context (marketing pages, long data
stories). Add `.neimo-header-meta` to the right side:

```html
<header class="neimo-header">
  <a class="neimo-header-mark" href="https://neimo.ai" …>…</a>
  <div class="neimo-header-meta">
    <span>Regulatory Intelligence</span>
  </div>
</header>
```

```css
.neimo-header { justify-content: space-between; }
.neimo-header-meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--dim);
}
```

No pulse dot. No two-line meta. The default is restraint — earn each extra
element.

**Sticky variant** for marketing pages where the header needs to persist:

```css
.neimo-header--sticky {
  position: sticky;
  top: 0;
  background: rgba(12, 7, 20, 0.72);   /* dark variant */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--rule);
  max-width: none;
  padding: 14px 64px;
}

@media print {
  .neimo-header--sticky {
    position: relative;
    background: transparent;
    backdrop-filter: none;
  }
}
```

**Placement by mode:**

| Mode | Header treatment |
|------|------------------|
| Client Blueprint | Quiet mark above hero slide |
| Data Story | Quiet mark above hero |
| Marketing Mock | Sticky variant with tagline |
| Presentation Deck | Cover-slide only; per-slide top bar carries the wordmark separately |
| Blog Diagram | Skipped — too compact; mark lives in footer only |

### k-ID Attribution Mark

Neimo is a k-ID product, so external deliverables carry both marks: Neimo as
the immediate maker, k-ID as the parent platform. The k-ID logo lives at
`assets/kid-logo.png` (white-on-transparent PNG) and is rendered via
CSS `mask-image` so it inherits `currentColor` — same coloring behavior as
the Neimo SVG wordmark.

```html
<span class="kid-logo kid-logo--small" role="img" aria-label="k-ID"></span>
```

```css
.kid-logo {
  display: inline-block;
  background-color: currentColor;
  -webkit-mask: url('assets/kid-logo.png') center / contain no-repeat;
          mask: url('assets/kid-logo.png') center / contain no-repeat;
  color: var(--muted);
  vertical-align: middle;
  flex-shrink: 0;
}

/* The k-ID shield is roughly square (~1.18:1) — set width = height.
   --small is slightly larger than wordmark cap-height so the shield's
   internal detail (kid + iD) stays readable in inline credit contexts. */
.kid-logo--small  { width: 16px; height: 16px; }
.kid-logo--inline { width: 20px; height: 20px; }
.kid-logo--large  { width: 28px; height: 28px; }
```

**For single-file deliverables** (the default), base64-encode the PNG and use
a data URI in `mask-image` so there's no external asset dependency:

```bash
# Generate the data URI string:
echo "data:image/png;base64,$(base64 -i assets/kid-logo.png)"
```

```css
.kid-logo {
  -webkit-mask: url('data:image/png;base64,iVBORw0KGgoAAAA…') center / contain no-repeat;
          mask: url('data:image/png;base64,iVBORw0KGgoAAAA…') center / contain no-repeat;
}
```

The same string goes in both `-webkit-mask` and `mask`. The base64 string for
the current shipping logo is in `assets/kid-logo.b64.txt` for paste-ready use.

### Powered-by Footer

Every Neimo-produced deliverable closes with a Powered-by mark. Treat it as
a product surface — the same way Stripe Checkout or a Linear-built dashboard
signs its work. Two patterns; pick by mode.

The footer carries both marks. Neimo leads as the product the customer is
seeing; k-ID follows as the platform that powers it. Reads as:
*neimo · powered by k-ID.* Matches the standard k-ID newsletter attribution.

**Pattern A — Inline footer line.** For document-feeling outputs: Client
Blueprint, Data Story, Blog Diagram. Sits inside the existing footer row.

```html
<div class="powered-by">
  <svg class="neimo-wordmark neimo-wordmark--small" viewBox="0 0 66 17"
       xmlns="http://www.w3.org/2000/svg" fill="none" aria-label="neimo">
    <path fill="currentColor" d="M1.39258 16.8345C…"/>  <!-- full path from Wordmark section -->
  </svg>
  <span class="powered-by-label">Powered by</span>
  <span class="kid-logo kid-logo--small" role="img" aria-label="k-ID"></span>
</div>
```

```css
.powered-by {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--muted);
}
.powered-by-label { color: var(--dim); }
```

**Sizing rationale:** the wordmark uses `--small` (11px) to match the
cap-height of the surrounding uppercase mono text, so it reads as part of
the line, not a logo dropped in. The k-ID shield uses `--small` (16px),
slightly taller than the text — needed because the shield is a complex mark
that's unreadable below ~14px. The asymmetry is intentional: line up to the
text where possible, override only when the mark requires it.

The Neimo wordmark inherits `var(--purple)` from `.neimo-wordmark` because
it's the product the reader is engaging with. The k-ID logo inherits
`var(--muted)` from `.kid-logo` because it's the platform stamp underneath,
not the foreground brand.

**Pattern B — Floating chip.** For canvas-style outputs: Marketing Mock,
Presentation Deck cover. Fixed bottom-right, sits over content like a
watermark. Clickable.

```html
<a class="neimo-chip" href="https://neimo.ai" target="_blank" rel="noopener">
  <svg class="neimo-wordmark neimo-wordmark--small" viewBox="0 0 66 17"
       xmlns="http://www.w3.org/2000/svg" fill="none" aria-label="neimo">
    <path fill="currentColor" d="M1.39258 16.8345C…"/>
  </svg>
  <span class="powered-by-label">Powered by</span>
  <span class="kid-logo kid-logo--small" role="img" aria-label="k-ID"></span>
</a>
```

```css
.neimo-chip {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: 100px;
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--muted);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 100;
  transition: transform 0.2s, border-color 0.2s;
}
.neimo-chip:hover {
  transform: translateY(-1px);
  border-color: rgba(165, 123, 245, 0.32);
}
.neimo-chip .powered-by-label { color: var(--dim); }

@media print {
  .neimo-chip {
    position: absolute;
    bottom: 24px;
    right: 24px;
    backdrop-filter: none;
  }
}
```

**Placement by mode:**

| Mode | Pattern | Position |
|------|---------|----------|
| Client Blueprint | A | Last slide footer row |
| Data Story | A | Bottom footer below final section |
| Blog Diagram | A | Below the graphic, in the caption row |
| Marketing Mock | B (chip) | Fixed bottom-right corner of page |
| Presentation Deck | B on cover only; per-slide footer carries `neimo` wordmark from slide 2 onward | Cover bottom-right; slide footers thereafter |

**The mark is required on every externally-shared deliverable.** Internal
drafts can omit it but should default to including it. The point is
recognizability — every Neimo-shipped artifact should be identifiable from a
thumbnail.

### Data Visualization

All charts are hand-built CSS/SVG. Never use Chart.js, D3, ApexCharts, or any
charting library. This keeps assets print-safe, on-brand, and dependency-free.

### Scroll Animation (for web-viewed assets)

```javascript
(function() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -30px 0px' });
  document.querySelectorAll('.anim, .anim-scale').forEach(el => io.observe(el));
})();
```

```css
.anim {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.anim.visible { opacity: 1; transform: none; }

.anim-scale {
  opacity: 0;
  transform: scale(0.92);
  transition: opacity 0.7s ease, transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}
.anim-scale.visible { opacity: 1; transform: scale(1); }
```

---

## Mode 1: Client Blueprint

For integration blueprints, one-pagers, and client-facing technical
deliverables. The "memorandum meets keynote" look.

### Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400;1,8..60,600&display=swap');
```

| Font | Role |
|------|------|
| **Sora** | Headings (800), subheads (600), body (400) |
| **JetBrains Mono** | Labels, tags, badges, code, API references |
| **Source Serif 4** | Italic accent inside `<em>` in headings |

### Color Tokens

```css
:root {
  --void: #FCFBFF;
  --deep: #F7F6FE;
  --panel: #FFFFFF;
  --panel-raised: #F3EDFE;
  --rule: rgba(112, 38, 249, 0.12);
  --white: #1B1B25;        /* heading text (named for dark-mode origin) */
  --text: #3A3850;
  --muted: #5F5F71;
  --dim: #81818B;
  --purple: #7026F9;       --purple-glow: rgba(112, 38, 249, 0.06);
  --teal: #4264D1;         --teal-glow: rgba(66, 100, 209, 0.08);
  --coral: #AF7EFF;        --coral-glow: rgba(175, 126, 255, 0.08);
  --sky: #6CE2FF;
  --green: #30A46C;        --green-glow: rgba(48, 164, 108, 0.06);
  --red: #E5484D;
}
```

### Layout

Vertical slide deck. Each section is a full-viewport "slide":

```css
.slide {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 64px;
  position: relative;
  max-width: 1080px;
  margin: 0 auto;
}
```

Slide dividers between sections:

```css
.slide-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--rule), transparent);
  max-width: 1080px;
  margin: 0 auto;
}
```

### Section Chrome

```css
.slide-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  margin-bottom: 16px;
}

.slide-heading {
  font-size: clamp(2rem, 4.5vw, 3rem);
  font-weight: 800;
  color: var(--white);
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 20px;
  max-width: 700px;
}

.slide-heading em {
  font-family: 'Source Serif 4', serif;
  font-style: italic;
  color: var(--purple);
}
```

### Client Customization

Swap the body font and base surface to match the client's brand warmth:

| Client vibe | Body font | Base surface | Rule color |
|-------------|-----------|-------------|------------|
| Default (cool) | Sora | `#FAFAFE` | `rgba(112, 38, 249, 0.12)` |
| Warm (e.g. Kindred) | Satoshi (Fontshare) | `#F5F0E8` cream | `rgba(140, 100, 40, 0.10)` |

Kindred-style warm overrides:

```css
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap');

:root {
  --cream: #F5F0E8;
  --cream-deep: #EDE6DA;
  --paper: #FDF8F3;
  --rule-warm: rgba(140, 100, 40, 0.10);
  --kindred-green: #3ACE67;
  --kindred-cyan: #50DCFF;
}
body { font-family: 'Satoshi', sans-serif; background: var(--cream); }
```

### Reference Files

- Multi-slide scrolling: `family-pod/projects/characterai/resources/data-lite-mode-onepager.html`
- Multi-slide blueprint: `family-pod/projects/characterai/resources/integration-blueprint.html`
- Warm client variant: `family-pod/projects/kindred/resources/integration-blueprint.html`
- Single-page light: `family-pod/projects/inworld/resources/compliance-harness-onepager.html`

---

## Mode 2: Data Story

For narrative scroll pages that tell a data-driven market story (Brazil impact,
IDV proof, compliance metrics). Long-form with charts and editorial sections.

### Fonts

Same as Client Blueprint: **Sora + JetBrains Mono + Source Serif 4**.

### Color Tokens

Same `:root` variables as Client Blueprint. Supports light and dark variants:

**Dark variant** (for "visual authority"):

```css
:root {
  --void: #0C0714;
  --deep: #1A1229;
  --panel: rgba(255, 255, 255, 0.04);
  --panel-raised: rgba(255, 255, 255, 0.06);
  --rule: rgba(112, 38, 249, 0.12);
  --white: #F5F2FF;
  --text: rgba(255, 255, 255, 0.72);
  --muted: rgba(255, 255, 255, 0.48);
  --dim: rgba(255, 255, 255, 0.32);
}
```

### Layout

Long narrative scroll. Sections are NOT full-viewport — they use padding-based
spacing and flow naturally:

```css
section {
  position: relative;
  width: 100%;
}

.constrain {
  max-width: 1080px;
  margin: 0 auto;
  padding-left: 64px;
  padding-right: 64px;
}
```

Sections typically use `padding: 100px 0` and linear-gradient backgrounds
between `--void` and `--deep`.

### Section Chrome

```css
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin-bottom: 12px;
}

.section-heading {
  font-size: clamp(1.6rem, 3.5vw, 2.4rem);
  font-weight: 700;
  color: var(--white);
  letter-spacing: -0.02em;
  margin-bottom: 16px;
  line-height: 1.2;
}
```

### Hero (Data Story)

```css
.hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 80px 64px;
  background:
    radial-gradient(ellipse 50% 45% at 30% 30%, rgba(112, 38, 249, 0.06), transparent),
    radial-gradient(ellipse 50% 45% at 70% 70%, rgba(108, 226, 255, 0.05), transparent),
    var(--void);
}

.hero-title {
  font-size: clamp(2.6rem, 5.5vw, 4rem);
  font-weight: 800;
  color: var(--white);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.hero-accent {
  font-family: 'Source Serif 4', serif;
  font-style: italic;
  font-weight: 700;
  color: var(--purple);
  font-size: clamp(2.8rem, 6vw, 4.2rem);
  display: block;
}
```

### Reference Files

- Full dark story: `docs/brazil-data-pack/brazil-impact-story-v2.html`
- Full light story: `docs/brazil-data-pack/brazil-impact-story-light-v2.html`
- Short dark narrative: `docs/brazil-data-pack/idv-impact-story.html`

---

## Mode 3: Presentation Deck

For full-bleed slide decks with rich data visualization — gaming impact packs,
market analysis, investor-style presentations.

### Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&family=Crimson+Pro:ital,wght@0,600;0,700;0,800;1,600&display=swap');
```

| Font | Role |
|------|------|
| **Outfit** | Headings (800), body (400–500) |
| **Space Mono** | Slide numbers, metrics, legends, data labels |
| **Crimson Pro** | Italic accent in cover titles |

### Color Tokens

Warm dark purple palette:

```css
:root {
  --bg-deep: #120A1F;
  --bg-slide: #18102A;
  --bg-card: #211736;
  --bg-card-alt: #281D42;
  --bg-card-glow: #2D2150;
  --border-subtle: rgba(175, 126, 255, 0.14);
  --border-active: rgba(175, 126, 255, 0.28);

  --text-bright: #FFFFFF;
  --text-primary: #F2EEFA;
  --text-secondary: #B7A9D6;
  --text-dim: #8D7BAF;

  --orange: #AF7EFF;
  --orange-bright: #C8A8FF;
  --orange-glow: rgba(175, 126, 255, 0.16);
  --teal: #6CE2FF;
  --teal-glow: rgba(108, 226, 255, 0.12);
  --blue: #8EA4FF;
  --purple-accent: #A57BF5;
  --coral: #715DEC;
  --green: #4ADE80;

  --bar-purple: #8B6CC1;
  --bar-orange: #AF7EFF;
  --bar-teal: #6CE2FF;
  --bar-blue: #8EA4FF;
  --bar-coral: #715DEC;
}
```

### Layout

Full-bleed slides with no max-width constraint:

```css
.slide {
  min-height: 100vh;
  padding: 56px 64px;
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--bg-slide);
}
```

Each slide gets its own radial gradient background via per-slide classes:

```css
.cover {
  background:
    radial-gradient(ellipse at 30% 20%, rgba(165, 123, 245, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(108, 226, 255, 0.08) 0%, transparent 50%),
    var(--bg-deep);
}
```

### Slide Number Badge

```css
.slide-number {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--orange);
  background: var(--orange-glow);
  border: 1px solid rgba(245, 165, 36, 0.2);
  display: inline-flex;
  padding: 4px 14px;
  border-radius: 100px;
  margin-bottom: 20px;
  width: fit-content;
}
```

### Cards

Larger border-radius (16px) and glow variant:

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 28px;
  position: relative;
  overflow: hidden;
}

.card-glow {
  background: linear-gradient(135deg, var(--bg-card-glow), var(--bg-card));
}
```

### Slide Footer

```css
.slide-footer {
  margin-top: auto;
  padding-top: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.7rem;
  color: var(--text-dim);
  font-family: 'Space Mono', monospace;
  border-top: 1px solid var(--border-subtle);
}
```

### Reference Files

- Gaming impact deck: `docs/brazil-data-pack/brazil-gaming-impact-pack.html`

---

## Mode 4: Blog Diagram

For single embeddable graphics — flow charts, decision trees, step timelines,
signal flows. Compact, no scroll, designed to work inside blog posts or
LinkedIn shares.

### Fonts

Same as Client Blueprint: **Sora + JetBrains Mono + Source Serif 4**.
Add Material Symbols Rounded for icons.

### Color Tokens

Same light tokens as Client Blueprint. Use `--purple`, `--teal`, `--orange`
semantically for branches and decision paths.

### Layout

Single constrained graphic, no slides:

```css
.graphic {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 28px 28px;
}
```

No `min-height: 100vh`. Content determines height.

### Decision Tree Pattern

Root node → connector → diamond decision → branch connectors → branch cards:

```css
.root-node {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: var(--panel-raised);
  border: 1.5px solid rgba(112, 38, 249, 0.18);
  border-radius: 8px;
}

.connector-down {
  width: 2px;
  height: 24px;
  background: rgba(112, 38, 249, 0.15);
  margin: 0 auto;
}

.diamond {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 14px 28px;
  background: var(--panel);
  border: 1.5px solid rgba(112, 38, 249, 0.2);
  border-radius: 6px;
  position: relative;
}
.diamond::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--purple);
  border-radius: 6px 6px 0 0;
}
```

Branch cards with color-coded top strips:

```css
.branch {
  border: 1px solid var(--rule);
  border-top: none;
  border-radius: 0 0 8px 8px;
  background: var(--panel);
  overflow: hidden;
}
.branch::before {
  content: '';
  display: block;
  height: 3px;
}
.branch--child::before { background: var(--teal); }
.branch--youth::before { background: var(--orange); }
.branch--adult::before { background: var(--purple); }
```

Branch labels as tiny mono pills:

```css
.branch-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.52rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 3px;
}
.branch-label--child { color: var(--teal); background: var(--teal-glow); }
.branch-label--youth { color: var(--orange); background: var(--orange-glow); }
```

### Reference Files

- Decision tree: `docs/brazil-data-pack/blog-signal-flow.html`
- Step timeline: `docs/brazil-data-pack/blog-feature-level-trigger.html`
- Stage diagram: `docs/brazil-data-pack/blog-feature-level-verification.html`

---

## Mode 5: Marketing Mock

For website page prototypes — homepage, product pages, landing pages. Uses a
different font stack and more conventional web patterns.

### Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
```

Single font family. JetBrains Mono only when showing code samples.

### Color Tokens

```css
:root {
  --purple: #7026F9;
  --purple-dark: #715DEC;
  --purple-light: #F3EDFE;
  --purple-bg: #F7F6FE;
  --teal: #4264D1;
  --teal-light: #EEF3FF;
  --navy: #1B1B25;
  --gray-50: #f9fafb;   --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;  --gray-300: #d1d5db;
  --gray-400: #9ca3af;  --gray-500: #6b7280;
  --gray-600: #4b5563;  --gray-700: #374151;
  --gray-800: #1f2937;  --gray-900: #111827;
  --white: #ffffff;
  --orange: #AF7EFF;
}
```

### Layout

Standard web page with fixed nav and sections:

```css
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

.nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--gray-200);
}
```

### Section Chrome

```css
.section-label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--purple);
  margin-bottom: 12px;
}

.section-title {
  font-size: 40px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.5px;
}
```

### Hero Pattern

```css
.hero {
  padding: 80px 0 60px;
  background:
    radial-gradient(ellipse 60% 45% at 20% 15%, rgba(112, 38, 249, 0.08), transparent),
    radial-gradient(ellipse 50% 40% at 85% 10%, rgba(108, 226, 255, 0.14), transparent),
    linear-gradient(180deg, var(--white) 0%, var(--purple-bg) 65%, var(--white) 100%);
}

.hero h1 {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -1.5px;
}

.hero h1 .rotate-word {
  background: linear-gradient(135deg, var(--purple), #AF7EFF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### Buttons

```css
.btn-primary {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  color: var(--white);
  background: var(--purple);
}

.btn-outline {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  border: 1.5px solid var(--gray-300);
  color: var(--gray-700);
  background: transparent;
}
```

### Reference Files

- Homepage: `docs/kid-website-stuff/pages/homepage.html`
- Product pages: `docs/kid-website-stuff/pages/agekit-page.html`, `cdk-page.html`
- Dark mid-section: `docs/kid-website-stuff/pages/agekit-plus-mid-sections-mockup.html`
- Code tabs: `docs/kid-website-stuff/pages/cdk-code-tabs-mock.html`
- Scenario table: `docs/kid-website-stuff/pages/cdk-scenario-table-mock.html`

---

## Component Library

Reusable components that work across modes. Adapt colors and fonts to the
active mode's tokens.

### Hero Lockup (Client Blueprint)

Logo pair + title + tag pills + confidential footer:

```html
<div class="slide hero">
  <div class="logo-lockup">
    <!-- Partner SVG --> <span class="lockup-x">&times;</span> <!-- Neimo SVG -->
  </div>
  <h1 class="slide-heading">Title with <em>italic accent</em></h1>
  <p class="slide-subhead">One-line description</p>
  <div class="hero-pills">
    <span class="hero-pill hero-pill--purple">LABEL ONE</span>
    <span class="hero-pill hero-pill--teal">LABEL TWO</span>
  </div>
  <div class="hero-footer">CONFIDENTIAL — PREPARED FOR [CLIENT]</div>
</div>
```

```css
.hero-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid;
}
.hero-pill--purple {
  color: var(--purple);
  border-color: rgba(112, 38, 249, 0.25);
  background: var(--purple-glow);
}
.hero-pill--teal {
  color: var(--teal);
  border-color: rgba(66, 100, 209, 0.22);
  background: var(--teal-glow);
}
```

### Card Grid (Border-as-Gap)

```css
.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--rule);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--rule);
}
.card-grid .card {
  background: var(--panel);
  padding: 28px;
  border-radius: 0;
  border: none;
}
```

For 3- or 4-column: `grid-template-columns: repeat(3, 1fr)` or `repeat(4, 1fr)`.

### Permission/Status Table

```css
.map-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid var(--rule);
  border-radius: 6px;
  overflow: hidden;
}
.map-table th {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  background: var(--panel-raised);
  padding: 10px 14px;
  color: var(--dim);
  text-align: left;
}
.map-table td {
  padding: 12px 14px;
  font-size: 0.8rem;
  border-top: 1px solid var(--rule);
}
```

Status tags inside tables:

```css
.tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.tag--on     { color: var(--green); background: var(--green-glow); }
.tag--locked { color: var(--purple); background: var(--purple-glow); }
.tag--off    { color: var(--red); background: rgba(229, 72, 77, 0.06); }
```

### Flow Diagram (Numbered Steps)

```css
.flow-steps {
  display: flex;
  align-items: stretch;
  gap: 0;
}
.flow-step {
  flex: 1;
  padding: 28px 20px;
  background: var(--panel);
  text-align: center;
  position: relative;
}
.flow-step + .flow-step { border-left: 2px solid var(--rule); }
.flow-step::after {
  content: '\2192';
  position: absolute;
  right: -11px;
  top: 50%;
  transform: translateY(-50%);
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  color: var(--purple);
  z-index: 1;
  background: var(--panel);
  padding: 2px;
}
.flow-step:last-child::after { display: none; }

.fs-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 12px;
}
```

### Horizontal Bar Chart

```css
.bar-row {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
}
.bar-label {
  width: 120px;
  flex-shrink: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text);
}
.bar-track {
  flex: 1;
  height: 32px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 2px;
  width: 0;
  transition: width 1.4s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  align-items: center;
  padding-left: 12px;
}
.bar-fill .bar-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--void);
}
```

Bar fill gradients (semantic colors):

```css
.bar-fill--purple { background: linear-gradient(90deg, #7026F9, #AF7EFF); }
.bar-fill--teal   { background: linear-gradient(90deg, #4264D1, #6CE2FF); }
.bar-fill--coral  { background: linear-gradient(90deg, #715DEC, #AF7EFF); }
.bar-fill--sky    { background: linear-gradient(90deg, #4264D1, #8EA4FF); }
```

Set width via CSS variable and animate with IntersectionObserver:

```html
<div class="bar-fill bar-fill--teal" style="--w: 84%">
  <span class="bar-value">84%</span>
</div>
```

In print CSS, force the width: `.bar-fill { width: var(--w) !important; transition: none !important; }`

### SVG Donut Chart

Hand-built with stroke circles:

```html
<svg viewBox="0 0 200 200" width="200" height="200">
  <circle cx="100" cy="100" r="70" fill="none"
    stroke="var(--border-subtle)" stroke-width="24" />
  <circle cx="100" cy="100" r="70" fill="none"
    stroke="var(--orange)" stroke-width="24"
    stroke-dasharray="440" stroke-dashoffset="176"
    transform="rotate(-90 100 100)"
    stroke-linecap="round" />
</svg>
```

`stroke-dasharray` = `2 * PI * r` (~440 for r=70). `stroke-dashoffset` controls
how much is "unfilled." Rotate -90deg so it starts from the top.

### JSON Code Block

```css
.json-block {
  background: #1B1B25;
  border-radius: 8px;
  padding: 28px;
  overflow-x: auto;
  position: relative;
}
.json-block pre {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  line-height: 1.6;
  color: #c4c4d0;
  margin: 0;
  white-space: pre;
}
.json-block .jk { color: #AF7EFF; }  /* keys */
.json-block .js { color: #30A46C; }  /* strings */
.json-block .jn { color: #715DEC; }  /* numbers */
.json-block .jb { color: #4264D1; }  /* booleans */
.json-block .jc { color: #5F5F71; font-style: italic; }  /* comments */

.json-label {
  position: absolute;
  top: 10px;
  right: 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  color: #5F5F71;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
```

Usage:

```html
<div class="json-block">
  <div class="json-label">Response</div>
<pre>{
  <span class="jk">"status"</span>: <span class="js">"active"</span>,
  <span class="jk">"age_bracket"</span>: <span class="js">"child"</span>,
  <span class="jk">"permissions"</span>: {
    <span class="jk">"chat"</span>: <span class="jb">true</span>,
    <span class="jk">"spend_limit"</span>: <span class="jn">0</span>
  }
}</pre>
</div>
```

### Callout / Quote

```css
.callout {
  padding: 28px 32px;
  background: var(--purple-glow);
  border-left: 3px solid var(--purple);
}
.callout p {
  font-family: 'Source Serif 4', serif;
  font-size: 1.1rem;
  color: var(--white);
  line-height: 1.55;
}
.callout strong { color: var(--purple); font-weight: 700; }
```

Teal variant: swap `--purple-glow` → `--teal-glow`, border → `--teal`.

### Stat Row

```css
.stat-strip {
  display: flex;
  gap: 2px;
  background: var(--rule);
  border-radius: 2px;
  overflow: hidden;
}
.stat-strip-item {
  flex: 1;
  padding: 32px 28px;
  background: var(--panel);
  text-align: center;
}
.stat-strip-item .num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 6px;
}
.stat-strip-item .label {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
```

### Proportional Band Chart

Colored bands in a single row showing share/proportion:

```css
.prop-bands {
  display: flex;
  height: 56px;
  border-radius: 3px;
  overflow: hidden;
}
.prop-band {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--void);
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
}
.prop-band--a { background: linear-gradient(135deg, #AF7EFF, #7026F9); flex-grow: 65; }
.prop-band--b { background: linear-gradient(135deg, #8EA4FF, #4264D1); flex-grow: 21; }
.prop-band--c { background: linear-gradient(135deg, #C8A8FF, #715DEC); flex-grow: 14; }
```

---

## What NOT to Do

| Don't | Do Instead |
|-------|------------|
| Use Chart.js, D3, or any charting library | Hand-build with CSS bars, SVG circles |
| Use emojis for icons | Material Symbols Rounded |
| Use gradients on text (except Marketing Mock hero) | Solid accent colors |
| Use drop shadows heavier than `0.03` opacity | `box-shadow: 0 2px 12px rgba(0,0,0,0.025)` |
| Use borders thicker than `1px` (except accent bars) | 1px borders, 3px accent bars only |
| Use font sizes below `0.46rem` | Minimum 0.5rem for legibility |
| Use rounded corners larger than `16px` | 6–16px range |
| Mix font stacks between modes | Pick one mode, use its full stack |
| Put background on `body` for multi-page | Background on each `.slide` or `section` |
| Set Neimo wordmark in sans-serif or non-italic | Source Serif 4 italic in `--purple` (Crimson Pro italic in Presentation Deck) |
| Use `<img src="logo.png">` for the wordmark | Inline `<span>` or inline `<svg>` so the mark recolors and stays single-file |
| Ship an external deliverable without the Powered-by mark | Include Pattern A (inline) or Pattern B (chip) per the placement table |
| Place the Powered-by chip top-left, top-right, or mid-page | Bottom-right corner only — same place every time |

---

## PDF Generation

When you need a PDF from any mode, follow the **html-slide-to-pdf** skill. It
covers Playwright setup, single-page vs. variable-height strategies,
screenshot+pdf-lib assembly, and the mandatory QA checklist.
