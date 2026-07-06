# Dutch words into seed.json

## fields

- `name` — copy the input name verbatim.
- `name_en` — accurate English translation. For multiple senses, comma-separate (e.g. "turn, occasion"). For proper nouns keep the name (e.g. "Amsterdam"). For letters like "a"/"b"/"s" use "(letter a)" etc.
- `domain` — pick ONE domain from the taxonomy below.
- `topic` — pick ONE topic that BELONGS to the chosen domain (see taxonomy).
- `pos` — part of speech, ONE of: `noun` `verb` `adj` `adv` `enum`.
  - `enum` = numerals, determiners/quantifiers, articles (twee, vijf, derde, een, de, alle, sommige, meerdere).
  - `adv` = adverbs, particles, interjections, conjunctions, prepositions, pronouns, negations (ja, nee, niet, geen, nog, ook, wel, nu, toch, soms, altijd, mezelf, daarom, ermee...).
  - else `noun` / `verb` / `adj`.
- `level` — ALWAYS the string `"a"`.
- `similarity` — ONE of:
  - `same` = spelled identically to its English translation with same meaning (arm, bed, hand, respect, sport, stress, internet, budget, media, feedback, extra, fit).
  - `universal` = internationalism/loanword recognizable across languages (app, laptop, podcast, online, metro, café, alcohol, museum, route, serie).
  - `soundex` = Dutch word that sounds like its English cognate (boek→book, adres→address).
  - `native` = ordinary Dutch word with no obvious English resemblance (default).
- `stem` — morphological root: strip separable/verbal prefixes (aan-, be-, ver-, ont-, ge-, uit-, in-, mee-, thuis-, terug-) and inflectional endings; for compounds use the head-noun root; for simple words the bare base. Keep it short and lowercase. Examples: begrijpen→"grijp", verandering→"ander", hardlopen→"loop", slaapkamer→"kamer", oplossing→"los".
- `article` — ONLY for `pos:"noun"`: `"de"` or `"het"`. Omit for non-nouns.
- `plural` — ONLY for `pos:"noun"` that have a plural: the ending pattern `"-en"`, `"-s"`, or `"-'s"` (or full irregular plural). Omit if not applicable (proper nouns, uncountables).
- `also` — ONLY if the input word has `forms`: join them with ", " into a single string (e.g. forms ["is","ben"] → "is, ben"). Omit if no forms.

## Domain → allowed topics

- agentic: acceptance, assess, common, control, direction, effort, influence, intent, manipulate, must, operation, pragmatic, prevention, produce, result, solution, style
- artifacts: accessories, appliances, building, buildparts, buildrooms, clothing, furniture, gesture, routines, tool, transport, utensils
- body: behave, body, bodypart, eating, gesture, headparts, health, limbs, live, mimic, style, talk, transform, voice, walk
- civil: business, clash, common, cook, cooking, deal, education, justice, leisure, service, travel
- core: binding, compare, content, control, effort, flow, group, influence, limit, overall, pattern, posess, potention, produce, sequence, structure, systain, thing, timeline
- culture: arts, customs, leisure
- experience: attitude, audio, emotion, feelings, perceive, scent, taste, visual
- food: dishes, drinks, ingredients
- knowledge: acquire, cooperate, knowledge, language, script
- language: communicate, compare, grade, multitude, negotiate, reason, relation, repeat, talk
- life: animals, bird, fruit, insect, plant, rodents, species, systain, tamed, tree, vegetables
- mental: acceptance, acquire, attitude, beauty, certainty, common, emotion, evaluation, fear, feelings, intellect, learn, memory, mental, perceiption, pleasure, reasoning, recognition, understanding, will
- nature: celestials, color, daypart, landscape, materials, metal, pure, season, seescape, stuff, substance, temperature, weather
- resource: building, consume, dispose, exchange, getting, measure, possess, trade
- socium: care, common, conflict, convince, cooperate, family, game, knowledge, negotiate, operation, promotion, recognition, talk, virtue
- spatial: angle, deformation, direction, distance, extent, impulse, linear, manipulate, materials, move, place, position, shape, spatial, stable, surface, surfacing, transfer, transform, up-down
- system: appearing, change, defect, disruption, duration, month, occurence, order, path, pattern, potention, power, progress, repeat, style, systain, timeline, timeunit

## Example items

{"name":"beurt","name_en":"turn","domain":"system","topic":"occurence","pos":"noun","level":"a","similarity":"native","article":"de","plural":"-en","stem":"beurt"}
{"name":"begrijpen","name_en":"to understand","domain":"mental","topic":"understanding","pos":"verb","level":"a","similarity":"native","stem":"grijp","also":"begrijp, begrijpt"}
{"name":"internet","name_en":"internet","domain":"knowledge","topic":"knowledge","pos":"noun","level":"a","similarity":"same","article":"het","stem":"internet"}
{"name":"twee","name_en":"two","domain":"core","topic":"group","pos":"enum","level":"a","similarity":"native","stem":"twee"}

Do NOT include an `id` field — it is assigned later.
