# SEO state

Working files for the daily SEO runs (the `seo-autopilot` and `seo-audit` skills).
robots.txt keeps search engines out of this folder. Nothing here is linked from the site.

- `context.md`: product facts, with the file or URL each comes from
- `keyword-map.csv`: one row per search query and the page that targets it
- `backlog.md`: the queue, best expected sign-ups per hour of work first
- `log.md`: one dated line per shipped change
- `ai-prompts.md`: questions buyers ask AI assistants, and what they answered
- `directories.md`: directories and listings, with copy ready to paste
- `reports/`: weekly reports

Install the skills in a new session with:

    npx skills add Illyism/seo-skills --skill seo-autopilot
    npx skills add coreyhaines31/marketingskills --skill seo-audit

(they install under `.agents/` and `.claude/`, which `.gitignore` keeps out of the site).
