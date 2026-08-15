# Review And Titles Output

Use this reference when the user asks for any combination of:

- review this spoken script from a professional creator perspective
- what should be optimized and why
- give me a revised full version
- help me name this article or post
- mark page breaks for recording, slides, or image-text cards
- create a short video description or summary blurb

## Default Response Shape

If the user asks for both critique and revision, prefer this order:

1. Short high-level assessment
2. Optimization points
3. Why each point matters
4. `口播版本`
5. `文字版本`
6. `视频简介`
7. Title options

If the user later says "just give me the revised full version" or "just mark the page breaks," stop explaining and give only that.

If the user does not specify only one format, assume they want a spoken version, a written version, and a short video description.

## How To Review This User's Scripts

Focus on:

- whether the hook enters the topic fast enough
- whether each page carries only one idea
- whether the transition from external trigger to personal reflection is clear
- whether the ending stays in the user's voice instead of becoming preachy
- whether the script is still performable out loud after revisions

## How To Explain Revision Reasons

Keep explanations concrete and creator-facing. Prefer:

- "这一段的问题是..."
- "这样改是为了..."
- "这一页需要更单一的功能..."

Avoid inflated theory language or generic writing advice.

## Page Marker Rule

When the user wants a page-based script, or when you are generating a `口播版本`, output the revised script with explicit page markers by default.

Preferred format:

- `【第1页：看到AI资讯】`
- `【第2页：焦虑】`

Use the user's own page labels when available.
If the user does not provide page labels, infer them and make sure every page has a short extracted title.

## Spoken Vs Written Split

`口播版本` should:

- keep spoken rhythm
- preserve breath-sized sentence flow
- include page markers by default
- give every page a short extracted title
- allow small repetition when it helps performance

`文字版本` should:

- keep the same core structure and claims
- remove unnecessary口语停顿感
- read more smoothly as a post, article, or note
- stay aligned with the page logic even if page markers are removed

`视频简介` should:

- be noticeably shorter than the `文字版本`
- preserve the core tension and purpose of the piece
- read like a concise post summary or video caption
- avoid turning into a title list or hashtag dump unless the user asks

## Titles

When suggesting titles for this user:

- avoid clickbait that feels too aggressive
- prefer titles with emotion, self-positioning, or practical tension
- give 3 to 6 options unless the user requests only one

Useful title angles:

- emotional tension: anxiety, confusion, uncertainty
- action turn: stop watching, start using
- account origin: why I started this account
- identity stance: a normal person in the AI era

## Revision Intensity

If the user says a previous edit changed too much:

- preserve original wording where possible
- make smaller structural moves
- keep the user's sentence rhythm
- only change what supports the stated optimization goal
