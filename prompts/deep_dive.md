You are generating a themed scrollable HTML deep dive page for a personal daily briefing.

Topic: {{TOPIC}}
Research findings with sources: {{RESEARCH}}
Source list: {{SOURCES}}

---

STEP 1 — CLASSIFY THE THEME

Before writing any HTML, classify the topic into exactly one of these theme families:

ANCIENT / ARCHAEOLOGICAL (Great Wall, Roman roads, pyramids, ancient civilizations)
→ Warm parchment tones, serif accents, earthy palette
→ --theme-bg: #FAF7F2
→ --theme-bg-secondary: #F2EDE3
→ --theme-accent: #8B4513
→ --theme-accent-muted: #F5ECD9
→ --theme-text: #2C1810
→ --theme-text-secondary: #6B4C3B
→ --theme-border: #D4B896
→ --theme-font-display: Georgia, 'Times New Roman', serif
→ --theme-font-body: Georgia, serif

INDUSTRIAL / MECHANICAL (shipping containers, engines, manufacturing, infrastructure)
→ Steel tones, monospace accents, utilitarian grid
→ --theme-bg: #F4F4F2
→ --theme-bg-secondary: #E8E8E4
→ --theme-accent: #E85D04
→ --theme-accent-muted: #FDE8DA
→ --theme-text: #1A1A1A
→ --theme-text-secondary: #555550
→ --theme-border: #C4C4BE
→ --theme-font-display: 'Courier New', Courier, monospace
→ --theme-font-body: system-ui, -apple-system, sans-serif

NATURE / BIOLOGICAL (seed banks, ecosystems, food, agriculture, animals)
→ Organic greens, earth tones, soft rounded shapes
→ --theme-bg: #F7FAF4
→ --theme-bg-secondary: #EDF4E7
→ --theme-accent: #2D6A4F
→ --theme-accent-muted: #D8EDDF
→ --theme-text: #1B2E22
→ --theme-text-secondary: #4A6741
→ --theme-border: #B7D4BE
→ --theme-font-display: Georgia, serif
→ --theme-font-body: system-ui, -apple-system, sans-serif

FINANCIAL / SYSTEMIC (credit scores, banking, capitalism, economic systems)
→ Clinical whites, sharp typography, data-dense
→ --theme-bg: #FAFAFA
→ --theme-bg-secondary: #F0F0F0
→ --theme-accent: #1A3A5C
→ --theme-accent-muted: #E0EAF4
→ --theme-text: #0A0A0A
→ --theme-text-secondary: #4A4A4A
→ --theme-border: #D0D0D0
→ --theme-font-display: system-ui, -apple-system, sans-serif
→ --theme-font-body: system-ui, -apple-system, sans-serif

SCIENTIFIC / TECHNOLOGICAL (refrigeration, electricity, computing, space)
→ Deep backgrounds, electric accents, precision layout
→ --theme-bg: #0D1117
→ --theme-bg-secondary: #161B22
→ --theme-accent: #58A6FF
→ --theme-accent-muted: #1C2D3F
→ --theme-text: #E6EDF3
→ --theme-text-secondary: #8B949E
→ --theme-border: #30363D
→ --theme-font-display: 'Courier New', Courier, monospace
→ --theme-font-body: system-ui, -apple-system, sans-serif

CULTURAL / SOCIAL (music genres, subcultures, social movements, art)
→ Bold typography, expressive color, personality
→ --theme-bg: #FFFEF9
→ --theme-bg-secondary: #F5F0E8
→ --theme-accent: #C1121F
→ --theme-accent-muted: #FAE0E2
→ --theme-text: #14110F
→ --theme-text-secondary: #5C4A3A
→ --theme-border: #DDD0C0
→ --theme-font-display: Georgia, 'Times New Roman', serif
→ --theme-font-body: system-ui, -apple-system, sans-serif

MYSTERIOUS / FORGOTTEN (lost civilizations, obscure history, forgotten technology)
→ Deep moody tones, muted gold accents, sense of excavation
→ --theme-bg: #0F0E17
→ --theme-bg-secondary: #1A1826
→ --theme-accent: #C9A84C
→ --theme-accent-muted: #2A2618
→ --theme-text: #EBEBEB
→ --theme-text-secondary: #9A9099
→ --theme-border: #3A3650
→ --theme-font-display: Georgia, serif
→ --theme-font-body: system-ui, -apple-system, sans-serif

---

STEP 2 — GENERATE THE HTML

Generate a single fully self-contained HTML file using the classified theme. Structure:

HEAD:
- charset, viewport meta tags
- Open Graph tags:
    <meta property="og:title" content="{TOPIC}">
    <meta property="og:description" content="{2-3 sentence teaser from research}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{{URL}}">
    <meta name="twitter:card" content="summary">
- Full CSS in a <style> block using the theme variables
- All theme variables defined in :root

BODY STRUCTURE:

1. Page header — feels like a designed cover:
   - Full-width, themed background, generous padding (3rem top/bottom)
   - Large topic title in --theme-font-display, 36px, color --theme-accent
   - Date and "Daily Rabbit Hole" label in small caps above the title
   - 2-sentence hook below the title — the most surprising thing about this topic
   - Share button in top-right corner: a small icon button that copies window.location.href to clipboard and shows "Copied!" tooltip on click

2. Chapter navigation — anchor links (no JavaScript):
   - Sticky horizontal scrollable row of anchor links styled as pill buttons
   - Links: <a href="#chapter-1">Origin</a> | <a href="#chapter-2">The Mechanism</a> | ... | <a href="#chapter-6">Sources</a>
   - Normal pill: --theme-bg-secondary background, --theme-text-secondary text
   - Hover: slightly darker background
   - Use :target CSS pseudo-selector to highlight the current chapter

3. Chapter content — all visible, scrollable:
   - Each chapter is a full section with id="chapter-{number}"
   - Eyebrow label (small caps, --theme-accent, 11px)
   - Chapter title (24px, --theme-font-display)
   - Subtitle / hook (16px, --theme-text-secondary, italic)
   - Body content: timelines, stat cards, surprise callouts, prose — all themed
   - Every factual claim has an inline superscript citation: <sup><a href="SOURCE_URL" target="_blank" style="color:var(--theme-accent)">[N]</a></sup>
   - 2-3 "explore further" sections at the bottom of each chapter (just text, no buttons)

4. Sources chapter (Chapter 6):
   - Numbered list of every source used
   - Each entry: publication name (bold) — article title as a clickable link — one sentence on what it contributed
   - Feels like a proper bibliography

CONTENT RULES:
- Lead every chapter with the most surprising fact, not the most obvious one
- At least one "Wait, what?" moment per chapter — a fact that reframes the whole topic
- Never state a fact without a source citation
- If a claim came from multiple sources, cite both
- Stat cards for numerical facts, timelines for historical sequence, callout boxes for controversies

DESIGN RULES:
- All colors from theme variables — never hardcode hex values in the component CSS
- Mobile-first, max-width 680px, centered
- No external fonts, no external libraries, no CDN dependencies
- The page must look intentionally designed for this topic — typography, spacing, and color should all reflect the theme family
- Dark themes (SCIENTIFIC, MYSTERIOUS) need extra care on contrast — all text must be readable
- Surprise callout boxes: left border 3px solid --theme-accent, background --theme-accent-muted
- Timeline dots colored --theme-accent
- Stat card numbers in --theme-accent
- Anchor nav styling: use :target pseudo-selector for subtle highlighting

INTERACTIVITY:
- Chapter sections use id="chapter-{number}" (e.g., id="chapter-1", id="chapter-6")
- Nav links are plain <a href="#chapter-N">Chapter Name</a> — no JavaScript needed
- Share button uses: onclick="navigator.clipboard.writeText(window.location.href); this.textContent='Copied!'; setTimeout(() => this.textContent='Share', 1500);"

OUTPUT: Return only the complete HTML. No explanation, no markdown fences, no commentary.
