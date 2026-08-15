---
name: personal-style-script-writer
description: Generate Chinese content in the user's personal style from rough outlines, notes, or fragmented ideas. Use this skill when the user wants content expanded into a polished draft with a `口播版本`, a `文字版本`, and a `视频简介` by default, especially for short video scripts, platform posts, account-introduction content, or page-based image-text posts that may also need targeted web research, page markers, title suggestions, and preservation of the user's tone, rhythm, and recurring expressions.
---

# Personal Style Script Writer

Use this skill when the user provides raw notes, an outline, or incomplete ideas and wants a finished draft that sounds like them rather than generic AI writing.

## What This Skill Does

This skill combines four jobs:

1. Extract the user's style from prior samples or explicit preferences.
2. Diagnose which facts, examples, or context are missing.
3. Fill the gaps with targeted research when needed.
4. Turn the result into a spoken-friendly script or platform-ready text.

## Inputs To Collect

Ask for missing inputs only when they materially affect the result. Otherwise make a reasonable assumption and state it briefly.

- Source material: outline, notes, bullets, transcript fragments, mind map, or draft.
- Style evidence: past posts, past scripts, chat logs, article samples, or a written style brief.
- Usage target: short video, long-form spoken script, article, carousel copy, livestream opening, etc.
- Platform or channel: Xiaohongshu, Bilibili, WeChat, video account, podcast, newsletter, etc.
- Goal: explain, persuade, teach, sell, provoke discussion, summarize, or tell a story.
- Output constraints: duration, word count, CTA, taboo topics, required viewpoints, or audience level.

If the user has not yet supplied stable style samples, write with a neutral but confident voice and mark the draft as a provisional style match.

## Workflow

### 1. Build Or Reuse A Style Profile

If the user supplies writing samples, first infer:

- sentence length tendency
- opening pattern
- transition habits
- emotional temperature
- abstraction vs example density
- preferred vocabulary
- repeated phrases or rhetorical moves
- closers and CTA habits

If the style is still unclear, use the template in [references/style-profile-template.md](references/style-profile-template.md) and fill only the fields you can support from evidence.

If the user provides a process note or revision history, treat it as high-value style evidence. It often reveals stronger signals than a polished final draft because it shows what the user removes, resists, or keeps.

If the user provides both an original draft and a final approved draft, compare them directly. The delta is often more useful than either version alone for learning voice, compression habits, and collaboration preferences.

### 2. Normalize The Raw Material

Turn the user's input into:

- core claim
- target audience
- supporting points
- missing facts
- missing examples
- questionable claims that need verification

When the notes are messy, preserve the user's actual ideas before improving wording.

For origin-story or self-positioning content, also identify:

- the real emotional starting point
- the external trigger or turning point
- the deeper problem beneath the surface topic
- the belief or method the user wants to stand for
- the reason this content is different from generic AI commentary

### 3. Research Only What Is Missing

Do targeted research for unstable or missing facts. Avoid broad unfocused searching.

Prioritize:

- recent facts, numbers, releases, pricing, timelines, and product details
- concrete examples that strengthen the user's point
- counterpoints or caveats if the topic is controversial

When research is used, clearly separate:

- verified facts
- plausible synthesis
- stylistic embellishment

### 4. Draft In Spoken Language

Default to spoken-first writing unless the user explicitly asks for a formal article.

For口播稿:

- prefer short breath-sized sentences
- keep one idea per sentence cluster
- avoid stacked subordinate clauses
- use natural pivots such as "但问题是", "更关键的是", "你会发现"
- keep the script performable out loud

See [references/output-modes.md](references/output-modes.md) for platform-specific output patterns.

When the user's samples show anti-generic preferences, prefer:

- real emotional progression over polished summary
- concrete triggers over abstract declarations
- restrained conviction over slogan-like language
- spoken transitions over neatly symmetrical writing
- self-observation over grand claims

When the user's final samples resemble the current first-featured article, also prefer:

- real usage pressure over abstract AI awe
- "缺少实操场景" and "没有真正吸收内化" type framing when the user's problem is input-heavy but practice-light
- starting from real personal needs rather than generic productivity doctrine
- "记录真实尝试" over "输出技术教程"
- growth through ongoing practice rather than one-time awakening language

If the user is drafting content that will later be paired with images, slides, or caption cards, write with page-level segmentation in mind. Each section should carry one core idea and should not mix multiple turns of the argument.

If the user is creating a spoken script, paginate it by default unless the user explicitly asks for a single unbroken script. Explicitly label page breaks in the output, and give each page a concise extracted title. Use a clear format such as:

- `【第1页：主题】`
- `【第2页：主题】`

Keep the page title aligned with the user's logic when they already defined it. If they did not define page titles, infer them from the script structure.
Each page title should summarize that page's main idea rather than repeat a generic label.

When the user is creating content for publishing rather than only rehearsal, generate two companion versions by default unless they ask for only one:

- `口播版本`: optimized for speaking aloud, paginated by default, with an extracted title for every page
- `文字版本`: optimized for reading on the page, keeping the same core logic but smoothing transitions and removing spoken-only padding
- `视频简介`: a compressed summary based on the `文字版本`, suitable for use as a video description, intro blurb, or post summary

### 5. Run A Style Match Check

Before finalizing, compare the draft against the inferred style profile:

- Does it sound like the user's normal cadence?
- Are there generic AI phrases that should be removed?
- Is the amount of explanation too high or too low for this user's style?
- Did research overpower the user's own point of view?

If style fidelity is weak, provide a tighter revision instead of defending the first draft.

If the user explicitly says "不要再润色了" or otherwise locks a final version, stop optimizing tone and preserve the user's wording except for direct formatting requests.

When prior original-to-final pairs exist, check whether the new draft is repeating patterns the user usually cuts, such as:

- overextended emotional enumeration
- repeated rhetorical reinforcement of the same point
- explanatory endings that turn into calls to action
- broad conceptual claims where the user prefers a grounded action sentence

## Output Format

Unless the user asks otherwise, return:

1. `口播版本`
2. `文字版本`
3. `视频简介`
4. A short note with:
   - assumed audience
   - any research-based additions
   - any style uncertainty that still needs examples from the user

When useful, also provide:

- a punchier hook version
- a more conversational version
- a shorter cut for 30 to 60 seconds
- title options
- page-labeled script blocks for recording and图文排版
- a professional optimization review with:
  - what to improve
  - why to improve it
  - a lighter-touch revised version

If the user asks for review plus revision, prefer this output order:

1. Short review
2. Optimization points and reasons
3. `口播版本`
4. `文字版本`
5. `视频简介`
6. Title options

## Guardrails

- Do not invent facts, statistics, or quotes.
- Do not force a dramatic tone if the user's samples are restrained.
- Do not smooth away the user's distinctive phrasing unless it hurts clarity.
- Do not overstuff the script with research just because tools are available.
- If the user asks for "像我说的话", optimize for voice fidelity over textbook completeness.
- If revision notes show the user repeatedly removing "宣言感", avoid inflated endings, self-branding language, and generic transformation claims.
- If the user is optimizing page by page, do not merge page purposes just to improve prose flow.
- If the user gives explicit replacement lines, treat them as higher priority than stylistic polishing.
- If the user asks for a final draft without further polishing, output their approved wording cleanly rather than re-improving it.
- When adding page markers, do not silently rewrite the script more than the user asked for.
- Do not let the `文字版本` drift into a different argument from the `口播版本`; they should be two renderings of the same core content.
- Keep the `视频简介` meaningfully shorter than the `文字版本`; it should summarize rather than restate.

## When To Read References

- Read [references/style-profile-template.md](references/style-profile-template.md) when the user starts providing sample texts or asks to define their voice.
- Read [references/input-template.md](references/input-template.md) when the user wants a reusable submission format.
- Read [references/output-modes.md](references/output-modes.md) when the requested deliverable is platform-specific or spoken-content-first.
- Read [references/case-first-feature-process.md](references/case-first-feature-process.md) when the user is writing account-introduction,首推, personal positioning, or "why I started" content and wants the draft to preserve authentic motivation and revision logic.
- Read [references/paged-script-collaboration-pattern.md](references/paged-script-collaboration-pattern.md) when the user is iterating a script page by page for video,图文,口播分镜, or slide-based delivery.
- Read [references/original-vs-final-patterns.md](references/original-vs-final-patterns.md) when the user provides both a rough source draft and a final approved version and you need to infer what they consistently cut, keep, or tighten.
- Read [references/review-and-titles-output.md](references/review-and-titles-output.md) when the user wants a script reviewed from a creator/operator perspective, wants the reasons behind revisions, or wants title suggestions together with the revised script.
- Read [references/final-first-feature-style.md](references/final-first-feature-style.md) when the user is writing first-featured content, account motivation content, or any piece that should reflect the latest settled preferences from `首推.md`.
