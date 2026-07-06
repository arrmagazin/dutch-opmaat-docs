# dutch-opmaat-docs

Dutch language learning reference content — served as raw files via the GitHub trees API.

## What's in this repo

| Folder | Format | Purpose |
|--------|--------|---------|
| `grammar/` | markdown | Graded grammar reference, organised from sub-word units up to complex sentences. See [grammar/CLAUDE.md](grammar/CLAUDE.md) for the content style and pedagogical principles. |
| `topics/` | markdown | Thematic vocabulary and phrase collections (conversation, daily life, housing, personal info, official Dutch, weather). |
| `dialogs/` | JSON | Structured conversation scenarios for use by the app's tutor flow. Not rendered as docs. |

## Grammar overview

The `grammar/` folder is split into six layers; each subfolder contains short markdown pages ordered by number.

| Folder | Layer |
|--------|-------|
| `0-particles/` | letters, sounds, morphology |
| `1-auxiliaries/` | discourse helpers and reference words (connectors, time, place, *er*, question words) |
| `2-parts-of-speech/` | pronouns, nouns, verbs, adjectives, adverbs, comparatives |
| `3-phrases/` | noun phrases, prepositional phrases, *te + infinitive*, participles |
| `4-modes/` | clause modes: indicative, negative, modal, narrative, imperative, interrogative, passive |
| `5-sentences/` | coordination, subordination, relative clauses, reported speech |

Pages carry a CEFR level marker (*(A1)*, *(A2)*, *(B1)*, *(B2)*) next to the title so learners can self-sequence.

## How the content is served

The opmaat app fetches this repo's structure via the GitHub trees API and renders it as a navigable tree. Each markdown page is loaded on demand from the raw GitHub URL.

- Tree endpoint: `https://api.github.com/repos/[REPO]/git/trees/main?recursive=1`
- Raw file base: `https://raw.githubusercontent.com/[REPO]/main`

Files starting with `_`, plus any file named `CLAUDE.md` or `INDEX.md`, are filtered out of the docs tree. Use those names for maintainer-only content.

## Conventions

- **File names**: `NN-kebab-case.md` where `NN` controls sort order. The numeric prefix is stripped for display.
- **Folder names**: `N-kebab-case/` for layered taxonomy. Don't renumber existing folders; that breaks bookmarks.
- **Markdown**: see [`.markdownlint.json`](.markdownlint.json) for active rules.
- **Cross-links**: use the app's URL form `[label](/#/grammar?doc=PATH/FILE.md)` so navigation stays inside the docs viewer.
- **Style and pedagogy**: see [grammar/CLAUDE.md](grammar/CLAUDE.md) before adding or revising content.

## Contributing

1. Pick the right folder by the *layer* your topic lives at.
2. Pick the next free `NN-` slot inside that folder.
3. Follow the page skeleton and style guide in [grammar/CLAUDE.md](grammar/CLAUDE.md).
4. Verify cross-links resolve and headings increment by one level at a time.
