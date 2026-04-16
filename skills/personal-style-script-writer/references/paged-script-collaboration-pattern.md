# Paged Script Collaboration Pattern

Use this reference when:

- the user is writing a script that will be split across pages, slides, cards, or visual panels
- the user explicitly defines page-level logic such as "第一页讲什么，第二页讲什么"
- the user is iterating by replacing lines section by section instead of asking for a full rewrite

This file captures a repeated preference in the user's collaboration style.

## Core Principle

The script is not only for speaking. It also needs to map cleanly onto later visual pages.

That means optimization should follow page purpose first, language smoothness second.

## Stable Page Logic In This Case

For the user's first featured content, the preferred six-part flow became:

1. Seeing AI-related information
2. Feeling anxiety
3. Explaining the source of the anxiety
4. Seeing a video and extracting the video's viewpoint
5. Adding the user's own reflection
6. Deciding what to do next

When similar content appears later, preserve the distinction between:

- outside trigger vs internal reflection
- emotion vs interpretation
- account purpose vs broader worldview

## Collaboration Rules Revealed By This Case

### 1. The user may reject structure explanations and want direct rewriting

If the user says they do not want page logic explained and instead want the script rewritten according to that logic, stop explaining the framework and directly produce the updated script.

### 2. The user often revises by explicit line replacement

When the user says a page should become a specific paragraph, treat that wording as near-final source material. Do not drift away from it unless asked.

### 3. Separate "video viewpoint" from "my viewpoint"

This matters for credibility and for page structure.

- the video page should state what the video said
- the next page should state what the user thought after watching it

Do not blur the two.

### 4. Remove automatic intro padding when the user rejects it

If the user says not to start with self-introduction such as "大家好，我是...", remove it and start from the topic directly.

### 5. Final means final

When the user says "不要再润色了，按我改的给我终稿", preserve the exact approved wording and only organize it cleanly.

## Writing Heuristics For Page-Based Scripts

- Each page should contain one main idea.
- The first sentence of each page should make that page's role immediately clear.
- Avoid carrying unresolved meaning from one page into the next unless it is an intentional cliffhanger.
- If a sentence belongs to two pages, rewrite or split it rather than forcing it into both.
- When the user will later add visuals, give them clear semantic blocks rather than one long flowing monologue.

## Language Preferences Revealed Here

- direct topic opening is acceptable
- "感兴趣" can be better than "兴奋" when the user wants a calmer and more believable tone
- concrete anxiety framing such as "毕业即失业" is preferred over abstract unease when the user explicitly chooses it
- "了解和观望" vs "真正用起来" is a useful contrast for this user

## Assistant Behavior To Avoid

- re-polishing after the user has fixed the wording
- turning page-based copy back into essay flow
- adding extra emotional uplift at the end
- reintroducing generic AI phrases after the user removed them
