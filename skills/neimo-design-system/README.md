# Neimo Visual Design System — Claude Skill

A drop-in design skill that teaches Claude how to produce every visual asset
in Neimo's house style: client blueprints, data stories, presentation decks,
blog diagrams, and marketing mocks.

If you got here from the Neimo MCP onboarding, this is the matching design
system. Skill + MCP together is the full Neimo surface inside Claude.

---

## What's inside

```
neimo-design-system/
├── SKILL.md              ← The skill itself. Claude reads this when triggered.
├── README.md             ← This file.
├── assets/
│   └── neimo-logo.svg    ← The Neimo logo, used in headers and footers.
└── examples/
    └── brazil-data-story.html   ← Reference deliverable showing the system end-to-end.
```

---

## Installing in Claude

### Claude.ai (desktop, web, mobile)

1. Open Claude → Settings → Capabilities → Skills.
2. Click **Upload skill** and select the entire `neimo-design-system`
   folder (or the ZIP you downloaded).
3. The skill is now available. Claude will activate it automatically when you
   ask for any Neimo-styled visual ("data story", "client blueprint",
   "presentation deck", etc.) — or when you invoke it explicitly with
   `/neimo-design-system`.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R neimo-design-system ~/.claude/skills/
```

The skill is now available in every Claude Code session.

### Claude Projects (via API)

Upload the folder as a knowledge file in your project. Claude will read
`SKILL.md` whenever it's relevant to the task.

---

## How to invoke it

Anything visual, with the trigger phrases the skill expects:

> "Build me a data story on Brazil's loot-box rules"  
> "Make a client blueprint for the Kindred integration"  
> "Design a blog diagram explaining feature-level age gates"  
> "Use Neimo's design system to mock a marketing page for AgeKit+"

Claude will read `SKILL.md`, pick the right mode (Client Blueprint, Data
Story, Presentation Deck, Blog Diagram, or Marketing Mock), and produce a
single-file HTML deliverable that opens in any browser and exports to PDF
through Playwright.

---

## Swapping the Neimo logo

The skill ships with the official Neimo logo at `assets/neimo-logo.svg`,
configured with `fill="currentColor"` so it picks up the `--purple` token
and recolors automatically across light and dark variants. No setup required.

If you need to:

- **Replace it with a different version** (e.g. a co-branded lockup for a
  specific customer engagement), drop your SVG into `assets/neimo-logo.svg`,
  keeping the `fill="currentColor"` attribute on the main path.
- **Pin it to a specific color** instead of inheriting `--purple`, change
  `color: var(--purple)` on `.neimo-wordmark` in `SKILL.md`.
- **Use a PNG fallback** for environments that can't render SVG, the skill
  documents the base64 data-URI pattern in the Wordmark section.

The type-only wordmark (Source Serif 4 italic) remains documented as a
fallback for legacy environments where SVG isn't an option.

---

## Pairing with the Neimo MCP server

The MCP server gives Claude access to Neimo's structured regulatory data
(market profiles, compliance metrics, legal horizons). The skill teaches
Claude how to *visualize* that data in Neimo's house style. They're built
to be used together:

> "Use the Neimo MCP to pull Brazil loot-box compliance metrics, then build
> a data story in the Neimo design system."

Claude will query the MCP, get the numbers, and render them through this
skill. One round trip, one deliverable.

---

## Updating

We ship updates as new GitHub releases. To update, replace the folder with
the latest release ZIP. Your customizations to `assets/neimo-logo.svg` are
preserved if you keep that file.

---

## Support

Issues, feature requests, or wanting to ship a new mode → open an issue at
the GitHub repo, or reply to your Neimo onboarding thread.
