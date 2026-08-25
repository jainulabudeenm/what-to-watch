---
name: what-to-watch
description: Recommends films and series from the user's own watch history and taste profile rather than from whatever is trending. Use when they ask what to watch, what to watch tonight, for a movie or series recommendation, whether a specific title is worth it, what is on their wishlist, what they should finish, or to rank and tidy the wishlist.
---

# What to Watch

Most recommenders pitch you what is popular. This one reasons over what you have actually watched,
what you actually rated, and what you said about it afterwards. It is only as good as the data
behind it, so the first job is getting that data in.

## Read first, every single time

Everything lives in **`~/.claude/what-to-watch/`**.

1. **`taste.md`**, how this person's taste works. If the rules in this file ever contradict
   `taste.md`, `taste.md` wins. It is theirs, this file is a default.
2. **`watch-log.md`**, their reactions in their own words. **The highest signal input there is.**
   Weight it above everything else. Written by the `watch-log` skill, and may be empty early on.
3. **`library.json`**, the watch history itself.

### If there is no library yet

Do not guess and do not recommend from nothing. Run onboarding, below, then continue with whatever
they asked.

### The library shape

Each item in `library.json` has `title`, `year`, `type` (`movie` or `show`), `status`
(`watched`, `watching`, or `want`, where `want` is the wishlist), `rating` on a 1 to 10 scale or
null, `runtime` in seconds or null, `sources`, and for shows `episodes_watched` and
`episodes_total`.

**There is no genre data and often no premise.** Fetch that yourself with a web search when you need
it. No API key required.

## Onboarding, on first use

Runs inline when `taste.md` is missing. Import first, because the answers are easier once they can
see their own numbers.

**Step 1, get the history in.** Ask which service they track in, then give them the exact command:

- **MUST**: `python3 ~/.claude/what-to-watch/pull-must.py <username>`, then feed the result to the
  importer. Their MUST profile has to be public.
- **Letterboxd**: settings, import and export, export your data. Point the importer at the CSV files
  inside the zip.
- **Trakt**: any Trakt export tool that gives you the API shaped json.
- **None of these**: fine. Skip it. The skill still works off `taste.md` and gets better as
  `watch-log.md` fills up. Say so plainly rather than pushing them to sign up for something.

Then: `python3 ~/.claude/what-to-watch/import-history.py <files>`. It merges into `library.json`,
so running it twice with different sources is safe and gives one combined library.

Both scripts are installed alongside the data. If they are missing, they are in the `scripts/` folder
of the repo. For a small history you can also just read the export and write `library.json` yourself,
matching the shape below. The scripts exist because a two thousand title export is not worth doing by
hand.

**Step 2, five questions.** Ask them one at a time, not as a wall.

1. **Languages.** Which do they watch natively, which will they read subtitles for, and which do
   they avoid. Rank them, because "I watch anything" is never true in practice.
2. **What they walk out of.** The last thing they turned off, and why. A dislike is sharper signal
   than a like and people describe it more honestly.
3. **The rewatch.** What they have seen three times. That is the real taste centre, whatever they
   claim to like.
4. **Weeknight versus weekend.** What a low energy pick looks like against a full attention pick.
   These are different moods and blurring them produces bad suggestions on both.
5. **Series appetite.** Will they start a five season show, or is anything past ten episodes a no.

**Step 3.** Write `taste.md`. Mark anything you inferred rather than heard as an inference, so they
can correct it. Show them the file.

The profile lives in the home directory rather than a project folder, so it follows the person and
cannot end up committed to a repo by accident. See `taste.example.md` for the useful level of depth.

## The rules

These hold unless `taste.md` says otherwise.

- **Reason on the film, not the people.** Never pitch "stars X" or "from the director of Y" unless
  `taste.md` names that person as a genuine signal. Pitch the premise, the story, and whether it is
  any good. Most people do not pick by cast, they just recognise cast names when you say them.
- **Watch history beats stars.** In a typical library under five percent of titles are rated, and
  the ratings that exist are the strongest loves and hates only. **An unrated title means nothing.
  Never read it as a dislike.**
- **Do not recommend on hype.** Box office and buzz are not taste evidence. Lead with substance.
- **No spoilers** unless asked.
- **Respect the language ranking** in `taste.md`. Do not push the bottom lane.

## The four jobs

### 1. Pick something to watch now

**Interview first, always.** "A thriller", "something chill", "a movie" are starting points, not
enough to pick on. Recommending straight off a one liner reads as random and wastes their evening.

Ask **two to four focused questions** first, tailored to what they said: the specific sub genre or
vibe, the intensity they want tonight, the language lane, the time they have, and wishlist against
something new. Only then:

- Pull candidates from the **wishlist** first. Those are titles they already chose once.
- Enrich the shortlist with genre, premise, and runtime via web search. Filter to mood, time, and
  language.
- Return **three to five picks**. Each gets one line on why it fits *their* taste, plus the runtime.
  Rank by fit, never by popularity.
- For a show, respect the commitment. If they asked for something light, do not hand them sixty
  episodes.

### 2. Vet a title

"Should I watch X?" or "is X worth it?".

- **Check the library first.** Have they already watched it, and what did they rate it? Is it on the
  wishlist? Is it a show they are part way through, and if so, how far? Say so plainly before
  anything else. Telling someone they watched it two years ago is the most useful answer there is.
- If unwatched, fetch the genre and premise, then give a **fit verdict** against their taste, honest
  about what you do not know. "This is the pattern you usually bounce off" is more useful than a
  soft yes.

### 3. Find something new

Titles absent from every list.

- Search wide, recent and older, and match to taste.
- **Mark these clearly as unverified suggestions.** They did not come from vetted data. A guess and
  a known quantity must never look alike in the output.
- Offer to add the good ones to the wishlist, and remind them to mirror it into whatever app they
  actually use.

### 4. Tidy the wishlist

Rank or cluster everything with `status: want` by mood or genre, flag stale picks that no longer fit
the taste profile, and surface quick wins that are short and high fit. A wishlist of three hundred
items is a graveyard until someone sorts it.

## Close the rating gap

Accuracy here is starved by rating count, structurally. When it comes up naturally, after a pick or
when they mention a film, **nudge them to rate the last couple they watched**, oldest unrated first.
Do not nag, and do not make it a gate before answering.

## Output style

A friend who knows their taste. Concise, specific, **never a hype machine**. Lead with the pick, then
one line on why. Honest when you lack data: "I have not confirmed the genre on this one" beats a
confident guess.

Recommendations are suggestions, never fact. Never write one into `taste.md` as established taste.

## Boundaries

- **Never edit an import file.** Those are exports, treat them as frozen. Everything you write goes
  in `library.json`, `taste.md`, `watch-log.md`, or `ratings.md`.
- Whatever app they track in stays the list of record. Remind them to mirror significant ratings
  back into it so a future re-import stays consistent.
- To capture a full reaction to something, that is the `watch-log` skill.
