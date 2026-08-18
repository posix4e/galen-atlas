# Session queue — things worth raising with Zack

Working list. Newest findings at the top of each section. Items get promoted onto
`zcorner.html` when they're ready to discuss.

---

## Ready to discuss

### 1. Lemma 405 — a candidate *variant*, not a construal
Our best lead. The printed Greek is a single short link:

> Ἐπὶ αἵματος ἐμέτῳ φθόη καὶ τοῦ πύου κάθαρσις ἄνω
> ("after vomiting of blood, consumption and a purging of pus upwards")

Ḥunayn's Arabic gives a **five-step causal chain** in its place — vomiting of blood →
corruption → catarrh from the head → diarrhoea → retention of expectoration → death.
That is not translator's expansion; it is *more links than the Greek has*.

**Why it matters:** if the Arabic reflects an exemplar carrying the longer chain, this is
stemmatic evidence — exactly the category we have been claiming to look for and have not
yet found a real instance of. Aphorisms VII contains a run of these chain-aphorisms, so
transmission variance is plausible here.

**Ask Zack:** does the Arabic imply a Greek text with the fuller chain, or is Ḥunayn
importing the sequel from elsewhere in the book? Note the Arabic opens with
*thumma qīla baʿda hādhā* ("then it is said after this") rather than the usual
*qāla Abuqrāṭ* — a different formula, possibly marking continuation of a series.

### 2. Lemma 117 — the contrasting case, a clear *construal*
The Greek is telegraphic — hard-to-vomit patients, moderately fleshy, purge downwards,
hold back in summer. The Arabic spells the same content out as full clinical instructions
(more than twice the length) without adding anything not implied.

**Why it matters:** 405 and 117 together are the ideal teaching pair for the distinction
Peter drew. Same text, same translator, two completely different kinds of divergence.

### 3. Ḥunayn expands, and the numbers show it
Across 398 comparable lemmata, the median Arabic/Greek length ratio is **0.94**, but the
tails are lopsided: **29 lemmata where the Arabic is more than 1.4× the Greek, against
only 9 where it is under 0.6×.** Systematic expansion, quantified.

**Ask Zack:** is that the expected signature of Ḥunayn's technique, and does the skew
itself tell us anything about which exemplar he had? Also worth asking whether length
ratio is a defensible way to *screen* for candidate variants across a whole work, since
if it is, we can run it over every aligned text we hold.

---

## Next up

### 4. The Risāla, 130 sections
Ḥunayn's own account of what he translated, for whom, and what Greek manuscripts he
found. Nobody has it as structured data. The manuscript remarks bear directly on the
stemmatic question. Ask: is extraction tractable, and what fields would actually be
useful to a scholar rather than merely tidy?

### 5. *De nominibus medicis* — the prize
Arabic-primary, Greek lost, and no English has ever existed (a German version of 1931 is
all there is). The single best translation target in the corpus for someone with Arabic.
Wrong shape for occasional hours until the working relationship is proven — but worth
naming so he knows where this could go.

### 6. Does he read Hebrew?
Peter mentioned Greek and Arabic only. Our transmission map carries just two Hebrew
entries across ten receptions, and Galen reached Hebrew largely *through* Arabic. If he
has it, that branch is his; if not, it waits.

### 7. The sixteen Alexandrian summaries
We hold them, and nobody knows how they relate to the full works — what they compress,
what they drop, whether they follow the same lemma divisions.


### 10. Risāla §20 — what is it?
Our copy divides into 130 sections. Section lengths average 394 Arabic characters, but
**§20 runs to 2,975 — seven and a half times the mean**, with §16 and the preface close
behind. Ḥunayn wrote most where he had most to explain, and in the *Risāla* that usually
means the transmission was difficult: manuscripts he could not find, copies in poor
condition, translations he had to redo.

**Ask Zack:** which work is §20, and is the length doing what we think it is? If the
longest sections really do mark the messiest transmission, section length becomes a cheap
way to rank the whole corpus by how much trouble Ḥunayn had — which is a proxy, however
rough, for where the Greek tradition was already unstable in the ninth century.

### 11. *De crisibus* has no Ḥunayn translation in our holdings — only an epitome
Directly relevant to the ballot. For six works we hold an Alexandrian summary but **not**
Ḥunayn's full translation: *Adhortatio*, *De anatomicis administrationibus*, *De crisibus*,
*De naturalibus facultatibus*, *De temperamentis*, *De victu attenuante*.

*De crisibus* is the one that matters, because it is a live Phase 2 candidate **and** has
no English. If it wins the ballot, our Arabic support for it is a compressed teaching
epitome, not a translation — which is a much weaker witness and changes what collation
can even mean there. Worth knowing before the vote rather than after.

**Ask Zack:** does a Jawāmiʿ epitome carry any textual weight at all, or is it purely
reception? Peter's framing suggests the latter, but a summary made from a good exemplar
might still preserve something.

### 12. Six works where we hold both the translation and its epitome
*Ad Glauconem*, *De elementis*, *De pulsibus ad tirones*, *De sectis*, the *Aphorisms*
commentary, and *In Hipp. De officina medici*. Those pairs allow a controlled question:
what does an Alexandrian epitome actually drop? Same work, same language, two levels of
compression — and the *Aphorisms* pair is already lemma-aligned on our side.

---

## Our own bugs, for us not him

### 13. The manifest joins to the catalogue on free-text Latin titles
Cross-referencing Arabic holdings against the catalogue nearly produced a false report
that *De victu attenuante* was missing entirely. It isn't — the catalogue stores
`De Victu Attenuante` and the manifest `De victu attenuante`, and the join is
case-sensitive string equality on a human-typed field. Should join on work id. Caught
before it reached anyone, but it would have been an embarrassing thing to hand a scholar.

---

## Method questions worth his opinion

### 8. Grey literature defeats the catalogue
We nearly translated *On the Differences of Fevers* twice over: BBAW lists no translation
in any language, but a complete English version sits in a 1928 Edinburgh thesis. Our
verification gate is BBAW; that gate is demonstrably too narrow. Ask what a working
scholar actually checks.

### 9. Is the apparatus design sound before we build it?
We intend to record each divergence as structured data — what each witness reads, which
underlying Greek would account for it, and whether the claim is variant or construal.
Better to have it criticised on paper than after implementation.
