# The Speaking Answer Schema

One abstract pattern behind **all 108 model answers** ([Model speaking answers](/#/topics?doc=10-listings/32-Speaking_answers.md), source `data/speaking.json`), for the [Speaking exam](/#/topics?doc=09-exams_A2/60-Speaking.md).
Learn this schema and the glue words that fill it, and you can build any A2 speaking answer without inventing structure under time pressure.

## The universal schema

```
MOVE 1   ANSWER    [opener] + the question's own words          ~7 words
MOVE 2   DETAIL    [link]   + one extra fact                    ~7 words
MOVE 3   CLOSE     [stance] + want + reason                    ~11 words
```

**ANSWER · DETAIL · REASON.** Nothing else. What changes between answers is only which **glue word** opens each move.

What the corpus says — every number below counts all 108 answers:

| Invariant | Evidence |
|---|---|
| Exactly **3 sentences** | 108 of 108 — not one answer is 2 or 4 |
| About **26 words** total | 7.2 + 7.1 + 11.3 words per move |
| Move 1 **repeats the prompt's words** | 106 of 108 echo a content word; 87 echo two or more |
| Move 3 is the **longest** | the reason is where the words go |
| Every answer carries a **linking word** | 108 of 108 |
| The link sits in **move 3** | 104 of 108 — *want* 85, *ten slotte* 14, *maar* 4, *daarom* 1 |

### Move 1 — ANSWER · the openers

The opener is chosen by the **question type**, not by the topic. 52 answers use no opener at all: plain *Ik* + verb.

| Opener glue | Use it when | # | Example |
|---|---|---|---|
| *(none)* — **Ik** / **Mijn** + verb | a plain *wat / waar / hoe* question | 52 | Ik woon in Amsterdam. |
| **Ja,** … / **Nee,** … | a yes-no question (*Rijdt u vaak…? Heeft u…?*) | 8 | **Ja**, ik rijd vaak met de bus. |
| … **ook** … | the examiner told you their own case first | 6 | Ik vind Nederlands **ook** een moeilijke taal. |
| **liever** / **het liefst** | two pictures, you must choose | 13 | Ik ga **liever** naar een concert. |
| **het leukst** / **mooier** / **minder lekker** | choose by comparison | 9 | Ik vind drop **minder** lekker. |
| **Volgens mij** / **Ik denk dat** | you must guess about a picture | 4 | **Volgens mij** is het concert in een theater. |
| **Eerst** | three pictures, tell the story | 14 | **Eerst** moet David de banden controleren. |
| **Ik zou … willen** / **Mijn ideale …** | a wish question | 3 | Ik **zou** een vakantiehuis op Bali **willen** hebben. |
| **Veel Nederlanders** / **De Nederlandse** | asked about a Dutch custom | 3 | **Veel Nederlanders** vieren Sinterklaas. |

### Move 2 — DETAIL · the links

One extra fact, no new topic. 44 answers use no link word — the detail simply follows.

| Link glue | # | Example |
|---|---|---|
| **daar** / **er** — back to the place just named | 25 | Ik ga **daar** elke week naartoe. |
| **Daarna** — next step of the story | 14 | **Daarna** moet hij de olie controleren. |
| **Volgens mij** — the guessed half | 9 | **Volgens mij** moet hij ongeveer 10 minuten reizen. |
| **elke dag** / **… keer per week** | 9 | Ik drink **elke dag** twee kopjes koffie. |
| **ook** — add a second item | 8 | Ik drink **ook** thee. |
| **meestal** / **vaak** / **altijd** / **soms** / **nooit** | 8 | Ik kijk **meestal** thuis op de bank. |
| **dan** — then, in that case | 7 | Ik bel **dan** met mijn moeder. |
| **al … jaar** / **sinds** — how long | 5 | Ik woon daar **sinds** 2013. |
| **Zelf** — switch from other people to you | 3 | **Zelf** gooi ik mijn e-mails weg. |

What the detail is about: a **place** (50), **what you do** (38), **how often** (17), **with whom** (12), **when** (9).

### Move 3 — CLOSE · the reason

| Closer glue | # | Shape |
|---|---|---|
| **want** | 85 | `<stance>, **want** <reason>` — Ik neem de bus, **want** ik heb geen auto. |
| **Ten slotte** | 14 | ends the three-picture story instead of giving a reason |
| **maar** | 4 | `<other option> is ook goed, **maar** <your choice> is beter` |
| **daarom** | 1 | `**Daarom** moet zij vandaag lopen.` — conclusion instead of cause |

Before *want* comes a **stance**, almost never a bare fact: *ik vind …*, *ik hou van …*, *ik … graag*, *ik neem/doe/ga …*.

## Building an answer live

#### **Move 1 — steal the question's words.**

Turn *"Hoe vaak gaat u op vakantie?"* into *"Ik ga één keer per jaar op vakantie."* You do not invent a sentence, you re-use one.

Pick the opener from the question type:

- yes-no → **Ja,**
- two pictures → **liever**
- three pictures → **Eerst**
- guess → **Volgens mij**.

#### **Move 2 — add one fact and link it.**

> Where, when, how often, with whom.

Point back with **daar** / **er** / **dan**, or count with **elke dag** / **… keer per week**.

#### **Move 3 — always say why.**

- Stance + **want** + reason.
- If the task was a story, close with **Ten slotte** instead;
- if you compared two things, close with **maar**.

**Uitvoering** is the criterion that fails people: the question almost always has two parts and the second one is *waarom*. Move 3 exists to answer it — 85 of 108 model answers end in **want**.

## The 12 scenarios — one schema, different glue

Every answer is the same three moves; the scenario is just which glue you pick.

#### Scenario 1 — plain answer (28×)

- **ANSWER** Mijn moedertaal is Engels.  *(echoes* moedertaal *from the prompt)*
- **DETAIL** Ik spreek Engels en een klein beetje Nederlands.
- **REASON** Ik leer nu Nederlands, **want** ik woon in Nederland.

#### Scenario 2 — one picture, you must guess (15×)

- **OBSERVATION** Kirsten loopt op straat.
- **GUESS** **Volgens mij** is haar auto kapot.
- **CONCLUSION** **Daarom** moet zij vandaag lopen.

#### Scenario 3 — three pictures, tell the story (14×)

- **STEP** **Eerst** moet David de banden controleren.
- **STEP** **Daarna** moet hij de olie controleren.
- **STEP** **Ten slotte** moet hij de auto schoonmaken.

#### Scenario 4 — choose between two (13×)

- **PREFERENCE** Ik ga **liever** naar een concert.
- **DETAIL** Ik ga **meestal** samen met vrienden.
- **REASON** Ik doe dat **het liefst**, **want** ik hou van muziek en van dansen.

#### Scenario 5 — choose, but be fair to the other option (8×)

- **PREFERENCE** Ik woon **liever** in de stad.
- **DETAIL** In de stad zijn veel winkels en restaurants.
- **CONCESSION** Een dorp is rustig, **maar** de stad vind ik leuker, **want** daar is altijd wat te doen.

#### Scenario 6 — yes-no question (8×)

- **CONFIRM** **Ja**, ik rijd vaak met de bus.
- **DETAIL** Ik ga **elke dag** met de bus naar mijn werk.
- **REASON** Ik neem de bus, **want** ik heb geen auto en de bus is goedkoop.

#### Scenario 7 — how long already (8×)

- **STATEMENT** Mijn beroep is schoonmaker.
- **DURATION** Ik ben dat **al** drie jaar.
- **REASON** Ik werk **graag** als schoonmaker, **want** ik heb aardige collega's.

#### Scenario 8 — a Dutch custom, then you (6×)

- **NORM** **Veel Nederlanders** vieren Sinterklaas en geven elkaar een cadeau.
- **OWN PRACTICE** Ik vier Sinterklaas niet op 5 december.
- **REASON** Ik doe dat niet, **want** dat is geen traditie in mijn eigen land.

#### Scenario 9 — a wish (4×)

- **WISH** Ik **zou** een vakantiehuis op Bali **willen** hebben.
- **DETAIL** Op Bali is het altijd mooi weer.
- **REASON** **Ik wil** juist daar een huis, **want** ik hou van de zon en de zee.

#### Scenario 10 — something in the past (2×)

- **PAST EVENT** Ik heb **kort geleden** een paraplu gekocht.
- **CIRCUMSTANCE** Ik heb hem gisteren bij de HEMA gekocht.
- **REASON** Ik had een paraplu nodig, **want** het regent hier heel vaak.

#### Scenario 11 — a problem in the picture (1×)

- **PROBLEM** **Het probleem is dat** de koffie op het toetsenbord valt.
- **ADVICE** Paula **kan het beste** een nieuw toetsenbord kopen.
- **REASON** Zij moet dat snel doen, **want** zonder toetsenbord kan zij niet werken.

#### Scenario 12 — when does it happen, what do you do (1×)

- **TRIGGER** Ik ben wel eens te laat, **omdat** ik in de file sta.
- **RESPONSE** **Dan** bel ik mijn baas.
- **REASON** Ik bel altijd meteen, **want** mijn baas moet het weten.

## The four exceptions

Four answers put the linking word in move 2 instead of move 3 (765, 766, 767, 831), because their prompt asked a **third** thing that had to land in the last slot — e.g. 767 answers *where you live* + *contact with neighbours*, so the reason moves up:

- Ik woon in Amsterdam. / Ik heb weinig contact met mijn buren, **want** zij werken de hele dag. / Soms zeggen wij hallo op de trap.

The schema does not change — the reason is still there, only earlier. When a prompt asks three things, give each move one of them and attach **want** to whichever move carries the opinion.
