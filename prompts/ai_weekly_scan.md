You are generating a weekly AI industry digest as a self-contained, beautifully designed HTML page.

The inputs are:
- WEEK_RANGE: {{WEEK_RANGE}}
- RESEARCH: {{RESEARCH}}
- SOURCES: {{SOURCES}}
- URL: {{URL}}
- RECENT_COVERAGE: {{RECENT_COVERAGE}}

---

## THEME

Always use the SCIENTIFIC/TECHNOLOGICAL theme. This is the fixed identity of the weekly scan.

```css
:root {
  --theme-bg: #0D1117;
  --theme-bg-secondary: #161B22;
  --theme-accent: #58A6FF;
  --theme-accent-muted: rgba(88, 166, 255, 0.1);
  --theme-accent-warm: #F0883E;
  --theme-accent-warm-muted: rgba(240, 136, 62, 0.12);
  --theme-accent-red: #F85149;
  --theme-accent-red-muted: rgba(248, 81, 73, 0.1);
  --theme-accent-green: #3FB950;
  --theme-accent-green-muted: rgba(63, 185, 80, 0.1);
  --theme-accent-amber: #E3B341;
  --theme-accent-amber-muted: rgba(227, 179, 65, 0.1);
  --theme-text: #E6EDF3;
  --theme-text-secondary: #8B949E;
  --theme-border: #30363D;
  --theme-font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --theme-font-mono: 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace;
}
```

---

## HTML OUTPUT

Generate a complete, self-contained HTML document. No external fonts. No CDN. No JavaScript libraries. All CSS inline in a `<style>` block.

### HEAD

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="AI Weekly Scan: {{WEEK_RANGE}}">
<meta property="og:description" content="Major releases, research, open source, risks, policy, and community pulse across the AI ecosystem.">
<meta property="og:type" content="article">
<meta property="og:url" content="{{URL}}">
<meta name="twitter:card" content="summary_large_image">
<title>AI Weekly Scan: {{WEEK_RANGE}}</title>
```

---

### BODY STRUCTURE

#### 1. Page Header

Full-width header with dark gradient. Contains:
- Small eyebrow label: `AI WEEKLY SCAN` in `--theme-accent`, monospace, letter-spaced
- Title: `{{WEEK_RANGE}}` in large white text (36px desktop, 26px mobile)
- Subtitle: `AI ecosystem digest — releases, research, tools, risks, and what developers are talking about`
- Share button (top-right, circular): `onclick="navigator.clipboard.writeText(window.location.href);this.textContent='✓';setTimeout(()=>this.textContent='⬡',1500)"` — starts as `⬡`, changes to `✓`

#### 2. TL;DR Card

Place ABOVE the chapter nav. Full-width card with `--theme-accent-muted` background, `2px solid var(--theme-accent)` left border, `16px` left padding. Contains:
- Label: `TL;DR — THREE THINGS THIS WEEK` in monospace, `--theme-accent`, small caps
- Exactly 3 bullet points: the 3 most important developments of the week. Each bullet is one sentence. Bold the key noun (model name, company, concept).

#### 3. Chapter Navigation

Sticky horizontal scrollable pill nav. Pills link to each section anchor. Active state uses `:target` pseudo-selector on the section.

Pills (in order):
`Releases` | `Research` | `Open Source` | `Building` | `Risks` | `Policy` | `Benchmarks` | `Community` | `Learning` | `Enterprise` | `Try This`

#### 4. Chapters

Each chapter uses the same base structure:
```html
<section class="chapter" id="ANCHOR">
  <div class="chapter-header">
    <span class="chapter-eyebrow">EYEBROW TEXT</span>
    <h2 class="chapter-title">Section Title</h2>
  </div>
  <div class="chapter-content">
    <!-- items -->
  </div>
</section>
```

Each **item** inside a chapter:
```html
<div class="item">
  <div class="item-headline">
    <!-- optional: <span class="update-badge">📌 UPDATE</span> -->
    <a href="SOURCE_URL" target="_blank" rel="noopener">Headline text</a>
  </div>
  <div class="item-body">2–3 sentences. What happened. Why it matters.</div>
  <div class="item-meta"><span class="source-tag">Publication Name</span> <span class="date-tag">Date if known</span></div>
</div>
```

Use the `update-badge` span on any item that continues a story from RECENT_COVERAGE.

---

### CHAPTER SPECIFICATIONS

**🚀 MAJOR RELEASES** (id="releases", eyebrow="THIS WEEK IN AI")
- 3–5 items: new models, major version bumps, significant pricing changes
- Focus on concrete capability delta — what can you do now that you couldn't before?
- Include pricing per million tokens if changed

**📄 RESEARCH HIGHLIGHTS** (id="research", eyebrow="FROM THE LABS")
- 3–4 items: papers with a genuinely novel technique, significant benchmark result, or clear practical application
- For each: name the paper, the key innovation in one sentence, and why a practitioner should care
- Link to arXiv or primary source

**⚡ OPEN SOURCE PULSE** (id="open-source", eyebrow="GITHUB & HUGGING FACE")
- 4–5 items: repos with 500+ stars this week OR major updates to established projects
- Include repo name in `<code>` monospace tags
- State the star count or growth signal when known

**🛠️ HOW PEOPLE ARE BUILDING** (id="building", eyebrow="IN THE WILD")
- 2–3 items: real production patterns, agentic workflows gaining traction, integration approaches
- Source from developer blogs, HN threads, case studies — not vendor press releases
- Answer: who is doing this, what specifically are they doing, what made it work?

**🔴 RISKS & FAILURES** (id="risks", eyebrow="WHAT WENT WRONG")
- 2–4 items: safety incidents, production hallucinations with consequences, new jailbreak/exploit techniques, model vulnerabilities, AI systems behaving unexpectedly
- Use red/amber callout treatment: `border-left: 3px solid var(--theme-accent-red)`, `background: var(--theme-accent-red-muted)`
- Never omit this section even if light week — if minimal incidents, note what near-misses or theoretical risks were discussed

**⚖️ POLICY & REGULATION** (id="policy", eyebrow="RULES OF THE ROAD")
- 2–3 items: EU AI Act enforcement updates, US executive actions, China AI regulations, copyright lawsuits, congressional hearings
- For each: what changed, who it affects, what you should know for work
- Use amber callout for items that create near-term compliance obligations

**📊 BENCHMARKS & EVALS** (id="benchmarks", eyebrow="HOW THEY STACK UP")
- 2–3 items: new model comparisons on real tasks, leaderboard changes, eval methodology developments, API cost changes
- Use a small comparison table when ≥2 models are being compared:
  ```html
  <table class="bench-table">
    <tr><th>Model</th><th>Task</th><th>Score</th><th>Cost/1M</th></tr>
    ...
  </table>
  ```
- Answer the practitioner question: "should I switch?"

**🔥 COMMUNITY PULSE** (id="community", eyebrow="WHAT DEVELOPERS ARE SAYING")
- 3–4 items: what's being debated on HN, r/LocalLLaMA, Twitter/X — frustrations, workarounds, contrarian takes, grassroots discoveries
- Use quote-style items with a short pull-quote and source link
- This section captures the "vibe" that formal news misses — include the uncomfortable opinions

**🎓 LEARNING RESOURCES** (id="learning", eyebrow="WORTH YOUR TIME")
- 3–4 items: tutorials, deep-dives, or courses with demonstrable engagement (views, upvotes, reposts)
- For each: title, what you'll learn, why it's worth the time, link
- Prioritize practical over theoretical

**🏢 ENTERPRISE & FEATURES** (id="enterprise", eyebrow="TOOLS YOU USE")
- 3–4 items: new features in Microsoft Copilot, Claude Code, Cursor, GitHub Copilot, major cloud AI platforms
- Focus on features that affect developer or knowledge worker daily workflows

**💡 TRY THIS WEEK** (id="try", eyebrow="ACTION ITEM")
- Single item. One concrete thing to do this week.
- Could be: a model to swap into your workflow, a repo to clone and run, a technique to test, a prompt pattern to try
- Structure: **What** — **Why this week** — **How to start** (1–2 sentences with a specific starting point)
- Style as a full-width CTA box: `border: 1.5px solid var(--theme-accent)`, `background: var(--theme-accent-muted)`, `border-radius: 8px`, `padding: 20px`

**SOURCES** (id="sources", eyebrow="BIBLIOGRAPHY")
- Numbered list, one per source
- Format: `[N] **Publication** — [Title](URL) — one-sentence note on what it contributed`

---

### CSS RULES

Write a complete `<style>` block. Key rules:

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--theme-bg); color: var(--theme-text); font-family: var(--theme-font-body); line-height: 1.6; }

/* Page header */
.page-header { background: linear-gradient(135deg, #0D1117 0%, #161B22 60%, #1C2128 100%); border-bottom: 1px solid var(--theme-border); padding: 48px 24px 40px; text-align: center; position: relative; }
.page-eyebrow { font-family: var(--theme-font-mono); font-size: 11px; letter-spacing: 3px; color: var(--theme-accent); text-transform: uppercase; margin-bottom: 16px; }
.page-title { font-size: 36px; font-weight: 700; color: var(--theme-text); line-height: 1.2; margin-bottom: 12px; }
.page-subtitle { color: var(--theme-text-secondary); font-size: 15px; max-width: 540px; margin: 0 auto; }
.share-btn { position: absolute; top: 24px; right: 24px; width: 40px; height: 40px; border-radius: 50%; background: var(--theme-bg-secondary); border: 1px solid var(--theme-border); color: var(--theme-accent); font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; }
.share-btn:hover { background: var(--theme-accent-muted); }

/* TL;DR card */
.tldr-card { max-width: 680px; margin: 28px auto 0; padding: 20px 24px; background: var(--theme-accent-muted); border-left: 3px solid var(--theme-accent); border-radius: 0 6px 6px 0; }
.tldr-label { font-family: var(--theme-font-mono); font-size: 10px; letter-spacing: 2px; color: var(--theme-accent); text-transform: uppercase; margin-bottom: 12px; }
.tldr-card ul { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.tldr-card li { font-size: 14px; color: var(--theme-text); padding-left: 16px; position: relative; }
.tldr-card li::before { content: '→'; position: absolute; left: 0; color: var(--theme-accent); font-weight: 700; }

/* Chapter nav */
.chapter-nav { position: sticky; top: 0; z-index: 100; background: rgba(13,17,23,0.95); backdrop-filter: blur(8px); border-bottom: 1px solid var(--theme-border); padding: 10px 16px; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }
.chapter-nav::-webkit-scrollbar { display: none; }
.nav-pill { display: inline-block; padding: 5px 14px; margin-right: 6px; border-radius: 20px; font-size: 12px; font-family: var(--theme-font-mono); color: var(--theme-text-secondary); border: 1px solid var(--theme-border); text-decoration: none; transition: all 0.15s; }
.nav-pill:hover { color: var(--theme-accent); border-color: var(--theme-accent); }

/* Chapters */
.container { max-width: 680px; margin: 0 auto; padding: 0 20px 60px; }
.chapter { padding: 48px 0 32px; border-bottom: 1px solid var(--theme-border); }
.chapter:last-child { border-bottom: none; }
.chapter-header { margin-bottom: 28px; }
.chapter-eyebrow { font-family: var(--theme-font-mono); font-size: 10px; letter-spacing: 3px; color: var(--theme-text-secondary); text-transform: uppercase; display: block; margin-bottom: 8px; }
.chapter-title { font-size: 22px; font-weight: 700; color: var(--theme-text); }

/* Items */
.item { margin-bottom: 28px; padding-bottom: 28px; border-bottom: 1px solid var(--theme-border); }
.item:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.item-headline { font-size: 16px; font-weight: 600; margin-bottom: 8px; line-height: 1.4; }
.item-headline a { color: var(--theme-text); text-decoration: none; }
.item-headline a:hover { color: var(--theme-accent); }
.item-body { font-size: 14px; color: var(--theme-text-secondary); line-height: 1.7; margin-bottom: 10px; }
.item-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.source-tag { font-family: var(--theme-font-mono); font-size: 11px; color: var(--theme-text-secondary); background: var(--theme-bg-secondary); padding: 2px 8px; border-radius: 4px; border: 1px solid var(--theme-border); }
.date-tag { font-family: var(--theme-font-mono); font-size: 11px; color: var(--theme-text-secondary); }

/* Update badge */
.update-badge { font-family: var(--theme-font-mono); font-size: 10px; background: var(--theme-accent-amber-muted); color: var(--theme-accent-amber); border: 1px solid var(--theme-accent-amber); padding: 2px 7px; border-radius: 4px; margin-right: 8px; vertical-align: middle; }

/* Risk callouts */
#risks .item { border-left: 3px solid var(--theme-accent-red); background: var(--theme-accent-red-muted); padding: 16px; border-radius: 0 6px 6px 0; border-bottom: none; margin-bottom: 16px; }
#risks .chapter-title { color: var(--theme-accent-red); }

/* Policy amber callouts (optional class) */
.callout-amber { border-left: 3px solid var(--theme-accent-amber); background: var(--theme-accent-amber-muted); padding: 12px 16px; border-radius: 0 6px 6px 0; margin: 16px 0; font-size: 13px; }

/* Benchmark table */
.bench-table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 16px 0; font-family: var(--theme-font-mono); }
.bench-table th { text-align: left; padding: 8px 12px; background: var(--theme-bg-secondary); color: var(--theme-text-secondary); font-weight: 600; border-bottom: 1px solid var(--theme-border); font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
.bench-table td { padding: 8px 12px; border-bottom: 1px solid var(--theme-border); color: var(--theme-text); }
.bench-table tr:last-child td { border-bottom: none; }

/* Community quote */
.community-quote { font-style: italic; font-size: 14px; color: var(--theme-text-secondary); border-left: 2px solid var(--theme-border); padding-left: 14px; margin: 12px 0; }

/* Try This Week CTA */
#try .item { border: 1.5px solid var(--theme-accent); background: var(--theme-accent-muted); border-radius: 8px; padding: 20px; }
#try .item-headline a { color: var(--theme-accent); }

/* Source list */
.source-list { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.source-list li { font-size: 13px; color: var(--theme-text-secondary); padding-left: 28px; position: relative; }
.source-num { position: absolute; left: 0; font-family: var(--theme-font-mono); color: var(--theme-accent); font-size: 11px; font-weight: 700; }
.source-list a { color: var(--theme-text); }
.source-list a:hover { color: var(--theme-accent); }

/* Footer */
.page-footer { text-align: center; padding: 32px 24px; border-top: 1px solid var(--theme-border); font-family: var(--theme-font-mono); font-size: 11px; color: var(--theme-text-secondary); letter-spacing: 1px; }

/* Mobile */
@media (max-width: 480px) {
  .page-title { font-size: 26px; }
  .share-btn { top: 16px; right: 16px; }
  .chapter { padding: 32px 0 24px; }
}
```

---

### DEDUPLICATION

The `{{RECENT_COVERAGE}}` block lists stories covered in the past 3–4 weeks. For any item in your digest that matches a story in RECENT_COVERAGE:
1. Add the `update-badge` span before the headline
2. Lead the `item-body` with what is specifically NEW since that story was last covered
3. Do not include items from RECENT_COVERAGE unless there is a genuine new development

---

### CONTENT RULES

- Every factual claim must link to a real source from {{SOURCES}}
- No invented URLs. No placeholder links. If no source exists for a claim, don't make the claim.
- Lead each item with the most concrete detail, not the most obvious one
- The Risks section must always have content — even a light week has near-misses, theoretical discussions, or ongoing concerns worth noting
- Try This Week must be ONE thing — do not hedge with "you could also try..."
- No hype language: "revolutionary", "groundbreaking", "game-changing" — describe what it actually does
- Monospace font for: repo names, model IDs, API parameter names, benchmark scores

---

### FOOTER

```html
<footer class="page-footer">
  Sources: [N] web searches · Generated [YYYY-MM-DD] · AI Weekly Scan
</footer>
```

Replace [N] with the actual number of sources in {{SOURCES}}.

---

Return only the complete HTML document. No markdown fences. No explanatory text before or after.
