---
description: Set up or update your taste profile and import your watch history.
---

Run the Onboarding section of the `what-to-watch` skill in **update mode**.

If `~/.claude/what-to-watch/taste.md` already exists, read it first and ask only about what has
changed or what is missing. Do not restart the interview from scratch and do not overwrite anything
they did not mention.

If they want to refresh the watch history, re-run the importer. It merges into the existing
`library.json` rather than replacing it, so a second import is safe.

Show the updated file when you are done.
