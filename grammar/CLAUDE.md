# Grammar — maintainer guide

This file is for whoever maintains or extends the `grammar/` content (humans or Claude). It is filtered out of the opmaat app's docs tree by `apps/opmaat/src/utils/ghTree.ts`, so readers of the app never see it.

Three sections: how the folder is organised, how a page should look, and what teaching stance every page should take.

---

## 1. Repo structure & purpose

The `grammar/` folder is a graded reference for Dutch grammar, served as raw markdown to the opmaat app. Each subfolder covers one layer of the language; pages inside go from simpler to more complex.

```
0-particles/        sub-word units: letters, sounds, morphology
1-auxiliaries/      discourse helpers & reference words (connectors, time, place, er, question words)
2-parts-of-speech/  word classes: pronouns, nouns, verbs, adjectives, adverbs, comparatives
3-phrases/          phrase-level structures: noun phrases, PPs, te+inf, participles
4-modes/            clause modes: indicative, negative, modal, narrative, imperative, interrogative, passive
5-sentences/        complex sentences: coordination, subordination, relative clauses, reported speech
```

**Naming conventions:**

- Folders: `N-kebab-case/` where `N` is a single digit indicating the layer.
- Files: `NN-kebab-case.md` where `NN` orders the page inside the folder.
- The prefix digits get stripped for display by `prettifyName` in the app; keep them — they control sort order.
- `CLAUDE.md`, `INDEX.md`, and any file starting with `_` are filtered out of the docs tree. Use those names for maintainer-only content.

**Two legacy notes:**

- `1-auxiliaries/` is a historical name — its actual content is "discourse helpers & reference words". Do **not** rename the folder: existing bookmarks and any external links rely on the path. Future pages that fit this theme belong here.
- `1-auxiliaries/` skips `04-`. New files in this folder may take that slot or any unused number; don't renumber existing files.

**Adding a new page:**

1. Pick the right folder by what *layer* the topic lives at (sound → word → phrase → clause → sentence).
2. Pick the next free `NN-` number that puts it in the right reading order.
3. Follow the style guide below.
4. Cross-link from related pages.

**Adding a new folder:** only for a genuinely new layer. The current six are the intended taxonomy.

---

## 2. Content style guide

### Page skeleton

```markdown
# Page title  *(LEVEL)*

One-paragraph framing: what this is, why it matters, the single most useful thing to know.

## Top-level topic

Short prose intro.

| Dutch | English |
|-------|---------|
| ...   | ...     |

> Rule of thumb or warning.

### Subtopic

...

## Common mistakes

- ❌ *wrong form* → ✅ *right form* — one-line reason.
```

### Markdown conventions

- **H1** is the page title — exactly one per file. Append a level marker in italics: `# Verbs  *(A2)*`.
- **H2** for top-level topics inside the page.
- **H3** for subtopics. Use **H4** sparingly; if you need it often, consider splitting the page.
- **Italics** (`*woord*`) for Dutch words and phrases inline.
- **Bold** (`**woord**`) for the key term being introduced or highlighted inside an example.
- Ungrammatical forms: prefix with ❌ in mistakes lists, or wrap in `~~strikethrough~~` inline.
- Acceptable forms: prefix with ✅ in mistakes lists.
- **Blockquotes** (`>`) for rules of thumb, callouts, and warnings — not for examples.
- **Tables** for systematic comparison:
  - Two columns `| Dutch | English |` for translation pairs.
  - Three or more columns for rule + example + note layouts.
- **Code spans** (`` `...` ``) sparingly — only for things that look like code (path fragments, schematic formulas like `[det] [adj] [noun]`).

### Cross-links

Use the opmaat docs URL form so links work inside the app:

```markdown
[ER-word](/#/grammar?doc=1-auxiliaries/05-er-word.md)
```

The path is relative to the `grammar/` root, includes the leading number, and ends in `.md`. Always verify the target file exists before saving.

### Level markers

Place after the H1 title, separated by two spaces, in italics:

- `*(A1)*` — beginner survival; no inflection nuance assumed.
- `*(A2)*` — basic Dutch; can handle de/het, simple verbs, present + perfect.
- `*(B1)*` — intermediate; comfortable with subordinate clauses, modals, past narrative.
- `*(B2)*` — upper-intermediate; passive, reported speech, register variation.

A page may carry **one** primary level. If parts of the page reach into a higher level, mark those *sections* with the same italic note: `### Strong verbs  *(B1)*`.

### Length

- Target 60–200 lines per page.
- Shorter than 60: the topic probably belongs as a section inside a parent page; merge or cross-link.
- Longer than 200: consider splitting by subtopic and adding a thin parent page that links to the parts.

### `## Common mistakes` section

Every page ends with one. Format each item as a single line:

```markdown
- ❌ *Hij rent snelle* → ✅ *Hij rent snel* — adverbs don't inflect.
```

Pick mistakes that real learners actually make (especially English-speaker interference), not theoretical edge cases.

---

## 3. Pedagogical principles

These are the teaching stances every page should embody. When in doubt about a wording choice, defer to these.

**Front-load the rule.** State the operative rule in the first sentence or two. Show examples after, not before. Exceptions come last.

**Contrast with English where there's interference.** Word order (T-M-P vs. P-M-T), *toen* vs. *als* vs. *wanneer*, *want* vs. *omdat*, double-negative misconceptions — these are the high-value teaching moments. Name the English habit explicitly; don't just present the Dutch form.

**Use mnemonics where they exist.** `'t kofschip`, **V2**, **half-trap** (*half negen = 8:30*), **T-M-P**, *worden* vs. *zijn* for passive. Repeat the mnemonic on every page that touches the topic — don't make readers chase a single canonical source.

**Acknowledge register.** Where formal/informal, written/spoken, or NL/BE differ, say so briefly. Don't pretend Dutch is monolithic. Common cases: *jij/u*, *je/jou*, splitting er-words, verb-cluster ordering in subordinates.

**Common mistakes belong in the closing section, not buried.** A learner scanning a page should find the "what will I get wrong?" answer in a predictable place. One section, end of file, no exceptions.

**Cross-link rather than duplicate.** Each topic has exactly one home page. Other pages that brush against it carry a one-line bridge with a link. Example: `05-adverbs.md` mentions pronominal adverbs in two sentences and links to `1-auxiliaries/05-er-word.md` for the full treatment.

**Examples should look like real Dutch.** Use sentences a learner might actually say or hear. Avoid contrived "the boy gives the book to the girl" pedagogy when *Ik geef het boek even aan haar* makes the same point with softening particles a learner needs anyway.

**Soft particles are not optional decoration.** *Eens, even, maar, toch, hoor, wel, gewoon* — Dutch speech is full of them. Pages that touch the imperative, questions, or modality should show them in examples and name at least one in the prose.

**Tables for systematic patterns, prose for nuance.** A conjugation paradigm is a table. The reason a learner says *Ik ben gelopen* instead of *Ik heb gelopen* is a paragraph.

**One worked example per major topic.** If a page introduces a non-trivial pattern (passive, past narrative, subordinate word order), include at least one full sentence or short paragraph annotated with what each piece does.
