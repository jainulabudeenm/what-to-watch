---
name: watch-log
description: Captures reactions to films and series into ~/.claude/what-to-watch/watch-log.md, the judgment layer a tracking app cannot hold. Two modes, mine a notes or journal folder for screen mentions and propose entries, or log a reaction told directly ("just watched X, the second half landed, about an 8"). Use when the user says log my watches, update my watch log, scan my notes for movies, or tells you what they thought of something they just saw.
---

# Watch Log

A tracking app records **that** you watched something. It cannot record **what you thought**, which
is the only part that makes the next recommendation better.

This catches the opinion before it evaporates. The log lives at
**`~/.claude/what-to-watch/watch-log.md`** and is the highest signal input the `what-to-watch`
recommender has.

## Iron rule

**Never write to, or edit, the notes you are reading from.** Journals and personal notes belong to
the person who wrote them. This skill reads them and writes only to `watch-log.md` and
`ratings.md`, and only after the entries are approved.

It also **never surfaces non film content** it happens to read on the way. A journal entry is a
private thing that happens to mention a movie. Take the movie, leave the rest, and do not quote or
summarise the surrounding text back to them.

## Mode 1, mine a notes folder

1. **Find the folder.** Look for `notes-folder:` in the `watch-log.md` frontmatter. If it is not
   set, ask once for the path, then store it there. If they do not keep notes, say so and switch to
   Mode 2 instead of guessing at a location.
2. **Find new entries only.** Read `last-scanned:` from the frontmatter. Scan files dated newer than
   that, using the date in the filename where there is one. `never` means scan everything.
3. **Detect screen mentions.** Look only for a film or series they watched, plus any reaction.
   "Watched X", "finished Y", "rewatched Z", or an opinion about something. Ignore every other
   subject in the file.
4. **Match against the library.** Cross reference `library.json` by title and year to pick up the
   type and year. If a mention is not in the library, still propose it and flag that it is missing
   from their tracker.
5. **Propose, never write.** Show a table: watched date, title and year, **their reaction in their
   own words**, a score only where they clearly gave one, and which note it came from. Let them
   approve, edit, or drop each row.
6. **On approval:** append to `watch-log.md`, newest first. Add a `ratings.md` row for anything
   scored. **Bump `last-scanned:` to the newest date you scanned**, so the next run does not
   re-propose the same entries.

## Mode 2, direct capture

They just tell you: "watched Heat last night, the diner scene is the whole film, about a 9".

Match it against the library, append to `watch-log.md`, add to `ratings.md` if scored. No notes
folder involved, so `last-scanned` does not move. Quick confirm, then write.

## Quality bar

- **Their words, not yours.** The reaction column is their take. Quote it or paraphrase tightly. Do
  not smooth it, do not make it sound more considered, do not turn a shrug into a review.
- **Do not over infer a score.** "Loved it" is not a number. Leave the score blank unless they gave
  one or it is unmistakable. A reaction with no score is still valuable.
- **No duplicates.** Search `watch-log.md` for the title first. If it is already there, update that
  row rather than adding a second one.
- A reaction they confirmed is ground truth for the recommender. A reaction you proposed is a draft
  until they confirm it. Never blur the two.

## File shape

```markdown
---
last-scanned: 2026-08-01
notes-folder: ~/notes/journal
---

| Watched | Title | Reaction | Score | From |
|---|---|---|---|---|
| 2026-07-28 | Heat (1995) | the diner scene is the whole film | 9 | journal 2026-07-29 |
```
