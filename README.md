# What to Watch

Two Claude skills that recommend films and series from **your** watch history instead of from
whatever is trending this week.

Every recommender you have used is pitching you the same twenty titles it pitches everyone. This one
starts from the two thousand titles you already got through, the handful you cared enough to rate,
and what you said about them afterwards.

## Install

In Claude Code, as a plugin. This is the one to use, because it brings both skills plus the
`/what-to-watch-init` and `/watch-log-scan` commands:

```
/plugin marketplace add jainulabudeenm/what-to-watch
/plugin install what-to-watch
```

From npm, which also covers Claude.ai and anywhere outside Claude Code. This installs both skills
and the importers, without the slash commands:

```
npx @jainulabudeenm/what-to-watch
```

Add `--project` to install into the current repo instead of your home directory, so you can commit
it and share it with a team.

## Use

```
> what should I watch tonight
```

First run walks you through importing your history and asks five questions about your taste. After
that it is instant.

It will ask you two to four questions back before it suggests anything. That is deliberate. "A
thriller" is not enough information to pick on, and a recommendation made off a one liner reads as
random.

```
> is Sinners worth it?
```

Checks your own library first. If you watched it in 2024 and gave it a 3, it will tell you that
before it says anything else. That answer alone justifies the import.

```
> just watched Heat, the diner scene is the whole film, about a 9
```

Goes straight into your watch log, which is the strongest signal the recommender has.

## Getting your history in

Three importers. All of them merge into one library, so you can run more than one.

**MUST** has no export button, so there is a puller for the public json API the app itself uses. No
login, no key. Your MUST profile has to be public.

```
python3 ~/.claude/what-to-watch/pull-must.py <username>
```

**Letterboxd**: settings, import and export, export your data. Unzip it and point the importer at
the CSV files. `watched.csv`, `ratings.csv` and `watchlist.csv` are the useful ones. Half star
ratings are doubled onto a 1 to 10 scale.

**Trakt**: any export tool that gives you the API shaped json. Watched, watchlist and ratings files
all work.

Then, whichever you used:

```
python3 ~/.claude/what-to-watch/import-history.py <files>
```

It writes `~/.claude/what-to-watch/library.json`, keyed on title plus year so two sources give you
one library rather than two half libraries. When sources disagree about how far you got, the one
that says you got further wins.

**None of the above?** Skip the import. The skills still work off your taste profile alone and get
sharper as the watch log fills up.

## The two skills

**`what-to-watch`** does four jobs: pick something for tonight, vet a title you are unsure about,
find something genuinely new, and tidy a wishlist that has grown into a graveyard.

**`watch-log`** captures what you thought. A tracking app records that you watched something. It
cannot record that the second half fell apart, which is the part that makes the next pick better. It
reads a notes folder if you keep one, proposes entries, and writes only what you approve. It never
edits your notes and never surfaces anything in them that is not about a film.

## Rules it will not bend

- **Reasons on the film, not the cast.** Never "from the director of", unless your profile names
  that person as a real signal.
- **An unrated title means nothing.** In most libraries under five percent of titles are rated. It
  will never read a blank as a dislike.
- **No hype.** Box office is not taste evidence.
- **A guess never looks like a known quantity.** Anything from outside your library is labelled as a
  suggestion.
- **No spoilers.**

## Your data

Everything is in `~/.claude/what-to-watch/`. Home directory rather than a project folder, so it
follows you and cannot end up committed to a repo by accident. Plain json and plain markdown, yours
to edit or delete.

Nothing is uploaded anywhere. The MUST puller reads a public profile, and the skill searches the web
for genre and runtime on specific titles. That is the extent of it.

See `taste.example.md` for the depth of profile that produces good picks.

## License

MIT
