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
   - 2-3 sentence hook below the title — the most surprising thing about this topic, written like magazine copy
   - Share button in top-right corner: a small icon button that copies window.location.href to clipboard and shows "Copied!" tooltip on click

2. Chapter navigation — anchor links (no JavaScript):
   - Sticky horizontal scrollable row of anchor links styled as pill buttons
   - Links: <a href="#origin">Origin</a> | <a href="#how-it-works">How It Works</a> | <a href="#by-the-numbers">By the Numbers</a> | <a href="#flex">[Flex Title]</a> | <a href="#modern-world">Modern World & Future</a> | <a href="#sources">Sources</a>
   - Note: "Flex" link text changes to the actual section title (e.g., "The Controversy", "The People", "The Science", etc.)
   - Normal pill: --theme-bg-secondary background, --theme-text-secondary text
   - Hover: slightly darker background
   - Use :target CSS pseudo-selector to highlight the current chapter

3. Chapter content — all visible, scrollable:
   - **Chapter 1: Origin** (id="origin")
     - Eyebrow: "THE BEGINNING"
     - Title: "Origin"
     - Lead with the earliest known moment or surprising origin story
     - Timeline from first appearance to present (or key historical arc)
     - Answer: Where did this thing come from? Who invented/discovered it? What was the first version?
     - At least one surprising historical fact

   - **Chapter 2: How It Works** (id="how-it-works")
     - Eyebrow: "THE MECHANISM"
     - Title: "How It Works"
     - Explain the fundamental mechanism, broken into digestible layers
     - Use diagrams/ASCII art if helpful, but prioritize clear prose
     - Answer: What is it? How does it actually function? What are its core components or steps?
     - Include at least one "Wait, that's counterintuitive" detail

   - **Chapter 3: By the Numbers** (id="by-the-numbers")
     - Eyebrow: "THE DATA"
     - Title: "By the Numbers"
     - Lead with the most striking statistic or trend
     - Stat cards: large number, label, one-sentence explanation with source
     - Timeline of growth, adoption, or key metrics
     - Charts represented as prose + ASCII if possible (or structured data readers can interpret)
     - Answer: What does the data tell us? Scale? Growth? Decline? Surprising disparities?

   - **Chapter 4: Flex — Choose Exactly One** (id="flex")
     - Pick the single most interesting angle for this specific topic from the list below
     - Eyebrow should match the flex type selected
     - Title should match the flex type selected
     - Lead with the most compelling fact for that angle

     **Option A: The Controversy** (for topics with dark sides, injustice, uncomfortable truths)
       - Eyebrow: "THE DARK SIDE"
       - Title: "The Controversy"
       - What ethical, moral, or safety concern surrounds this?
       - Who got hurt? What went wrong?
       - Is it being addressed?

     **Option B: The People** (for topics where the humans behind the thing are fascinating)
       - Eyebrow: "THE HUMANS"
       - Title: "The People"
       - Who are the key figures, inventors, or personalities?
       - What surprising detail makes them human?
       - How did their personality shape the thing?

     **Option C: The Science** (for deeper technical/scientific mechanisms)
       - Eyebrow: "THE SCIENCE"
       - Title: "The Science"
       - Layer deeper than Chapter 2 — the physics, chemistry, biology, or engineering
       - What does research tell us?
       - What's still not understood?

     **Option D: The Geography** (for topics about how something spread, shaped places, or varies by location)
       - Eyebrow: "THE MAP"
       - Title: "The Geography"
       - How did this spread geographically?
       - Are there regional variations or hotspots?
       - How did geography shape its evolution?

     **Option E: The Collapse** (for topics about failure, decline, or obsolescence)
       - Eyebrow: "THE DECLINE"
       - Title: "The Collapse"
       - When and why did it fail or decline?
       - What replaced it?
       - Are there lessons in the decline?

     **Option F: The Unintended Consequences** (for neutral or good things with unexpected ripple effects)
       - Eyebrow: "THE RIPPLES"
       - Title: "The Unintended Consequences"
       - What surprised everyone about how this thing spread or was used?
       - Positive side effects? Negative ones nobody expected?
       - How did it change society beyond its original purpose?

     **Option G: The Power & Money** (for topics about economics, control, and who gets rich)
       - Eyebrow: "FOLLOW THE MONEY"
       - Title: "The Power & Money"
       - Who got rich? Who lost?
       - How did the economics actually work behind the scenes?
       - Who controls it now? How much is it worth?

     **Option H: The Race** (for topics with competing standards, rival approaches, or losers)
       - Eyebrow: "THE COMPETITION"
       - Title: "The Race"
       - What were the competing approaches or standards?
       - Why did one win and others lose?
       - What was sacrificed in the victory?

     **Option I: The Everyday** (for abstract systems — zoom in on one person, object, or day)
       - Eyebrow: "ZOOM IN"
       - Title: "The Everyday"
       - Pick a specific person, object, or ordinary day
       - Show how this abstract thing touches concrete reality
       - Make it visceral and relatable

   - **Chapter 5: Modern World & Future** (id="modern-world")
     - Eyebrow: "NOW AND NEXT"
     - Title: "Modern World & Future"
     - What is the current state (present tense)?
     - How is it being used, debated, or evolved right now?
     - What's the trajectory? What's coming next?
     - Answer: Why does this still matter? What's the future?

   - **Chapter 6: Sources** (id="sources")
     - Eyebrow: "BIBLIOGRAPHY"
     - Numbered list of every source used
     - Each entry: publication name (bold) — article title as a clickable link — one sentence on what it contributed
     - Feels like a proper bibliography from a magazine feature

CONTENT RULES:
- **Magazine feature tone**: Write like someone who spent all night researching and is genuinely excited to share
- Lead every chapter with the most surprising fact, not the most obvious one
- At least one "Wait, what?" moment per chapter — a fact that reframes the whole topic
- Never state a fact without a source citation
- If a claim came from multiple sources, cite both
- Stat cards for numerical facts, timelines for historical sequence, callout boxes for surprises or controversies
- Use concrete details and vivid examples wherever possible
- Avoid jargon; explain specialized terms on first use

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
- Each section should feel distinct but cohesive — vary the visual presentation (prose vs. lists vs. callouts) to keep the reader engaged

INTERACTIVITY:
- Chapter sections use specific IDs: id="origin", id="how-it-works", id="by-the-numbers", id="flex", id="modern-world", id="sources"
- Nav links are plain <a href="#section-id">Section Name</a> — no JavaScript needed
- Share button uses: onclick="navigator.clipboard.writeText(window.location.href); this.textContent='Copied!'; setTimeout(() => this.textContent='Share', 1500);"

CHOOSING THE FLEX SECTION:
Before writing HTML, mentally evaluate the topic against each Flex option (a-i) and pick the ONE that is most interesting, surprising, or essential to understanding this topic. If the topic has a major controversy, choose The Controversy. If it's really about competing standards, choose The Race. Use your judgment to pick the angle that makes this topic most compelling.

OUTPUT: Return only the complete HTML. No explanation, no markdown fences, no commentary.
