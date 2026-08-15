---
name: gdpval-studio-dashboard
description: >-
  Builds and maintains a static "GDPval sample tasks" dashboard: a single-page site
  that browses real Mercor Studio task content (full tasks with exact prompt/rubric
  text and real downloadable input/golden-response files, plus lightweight prompt-only
  examples) grouped by occupation domain. A guided, beginner-friendly protocol: checks
  and helps set up git/GitHub/Vercel access, then asks the user which of four things
  they want to do (add tasks, redesign the UI, edit existing content, or deploy) and
  walks them through it in plain language, regardless of whether they're working in
  Claude Code, Cursor, opencode, a plain terminal, or any other agent. Use when the
  user runs /gdpval-studio-dashboard, asks to add or update tasks in a Studio
  sample-tasks dashboard, verify task content is word-for-word accurate, redesign its
  UI/theme, or deploy/redeploy it.
---

# GDPval Studio Dashboard — Build, Edit, Verify, Deploy

A static, no-build-step single-page app that renders real Mercor Studio task content
(prompts, rubrics, downloadable files) grouped by occupation domain. This skill is
written to be run by *any* AI coding assistant — Claude Code, Cursor, opencode, a
generic agent, or a person just following it by hand in a terminal — on behalf of a
user who may have **no technical background at all**. Assume nothing is known going
in; explain every term the first time it comes up, and never leave the user staring
at a raw error message without a plain-English translation of what it means and what
to do next.

**You are the one running commands and reading output — the human should almost
never need to touch a terminal themselves**, except for the handful of steps called
out below that genuinely require it (an interactive login, or your particular
environment not being able to run shell commands on the human's behalf at all). If
your environment *can* run shell commands directly, do that. If it can't (some
agent modes are read-only, or "chat only"), tell the human exactly what to paste into
a terminal, one command at a time, and wait for them to paste back the result before
giving the next one.

The single hardest-won rule underlying everything below: **every prompt and every
rubric description/rationale must be a word-for-word exact copy of the Studio source
— never paraphrased, condensed, or hand-transcribed.** Almost every gotcha in this
skill exists to protect that rule.

---

## Start here — every time this skill is used

Do these three things, in order, before anything else:

### 1. Confirm the project's files actually exist on this computer

This skill was originally built and run on one specific machine. Anyone using it on
a *different* computer will **not** have the project's files sitting there already
— they only exist (a) on that original machine, and (b) in the GitHub repository
it was pushed to. Don't assume the files are present; check first.

Look for a folder containing `index.html`, `data.js`, and a `files/` subfolder — try
the current working directory first, then a sensible project-named folder in the
home directory. If found, confirm the path out loud in one sentence ("Found the
project at `~/gdpval-sample-tasks`") and continue to step 2.

**If not found anywhere**, the human needs to download ("clone") a copy from GitHub
first. Explain it plainly:

> "This project's files live in a GitHub repository, not on this computer yet. I
> need to download a copy here before we can do anything else — that's a one-time
> step per computer."

Then get the repository URL — if you already know it (for this project, it's
typically `https://github.com/ananyaraghuwanshi-cloud/gdpval-sampletasks`, but
**confirm with the human rather than assuming**, since this skill may be reused for
a different copy/fork of the project), run:

```bash
git clone <repository-url>
cd <folder-name-it-created>
ls
```

Confirm `index.html`, `data.js`, and `files/` are now present before moving on. If
the human doesn't know the URL either, ask them to check wherever this project was
originally shared with them (a chat message, an email, a doc) — you cannot guess a
private repository's URL.

If `git clone` fails with a permission/access error, that's a sign the human's
GitHub account (see "Getting your accounts and tools ready" below) either isn't
logged in yet or hasn't been given access to that repository — flag that plainly
rather than retrying blindly.

### 2. Quietly check what's already set up

Run these checks yourself (don't ask the human to do this part — just run them and
read the results):

```bash
git --version                     # is git installed at all?
git config user.name              # has git been told who "you" are?
git config user.email
gh --version                      # is GitHub's helper tool installed?
gh auth status                    # is it logged in?
```

Don't narrate every command — just quietly gather the picture, then summarize
in one or two plain sentences ("Git's installed but not logged into GitHub yet" /
"Everything looks ready to go"). Save the detailed setup flow (below) for only if
something's actually missing, and only once you know what's missing.

### 3. Ask what they want to do today

Ask the human, in plain language, something like:

> "What would you like to do?
> **A)** Add new tasks to the dashboard (I'll fetch and format them from Studio links you give me)
> **B)** Change how the dashboard looks (colors, layout, style)
> **C)** Fix or update something that's already on the site
> **D)** Publish your changes so others can see them online"

Wait for their answer before doing anything else. If they're not sure, briefly
describe each in one sentence and let them pick — don't guess.

**Only if they pick D (or A/B/C but there's no local copy of the project on this
computer yet)**, walk through **"Getting your accounts and tools ready"** below
*first*, before the detailed steps for their choice.

---

## Getting your accounts and tools ready

Explain this part like you're talking to someone who has never used git before,
because they may not have. Two separate things are needed, for two separate reasons:

- **A GitHub account** — this is where the project's files are stored online, like a
  cloud folder with a history of every change. You need this so your changes can be
  saved and shared.
- **Access to the Vercel team that hosts the live site** — Vercel is the service that
  actually serves the website to visitors. You need to be added to the right team
  there (ask whoever set the project up originally to add you, by email or GitHub
  username, if you're not already a member).

Check, then fix only what's missing:

**If `git --version` failed or wasn't found:** git isn't installed. On a Mac, the
easiest way is:
```bash
brew install git
```
(If `brew` itself isn't found, that means Homebrew — a tool installer for Mac — isn't
set up either; point the human to https://brew.sh for a one-line install command
they can paste into Terminal, since that part does need to run interactively as
them.)

**If `git config user.name`/`user.email` came back empty:** git doesn't know who to
credit changes to yet. Ask the human for their name and the email they use on
GitHub, then run:
```bash
git config --global user.name "Their Name"
git config --global user.email "their@email.com"
```

**If `gh --version` failed:** GitHub's command-line helper isn't installed.
```bash
brew install gh
```

**If `gh auth status` shows not logged in:** this is the one step that must be done
*by the human, interactively* — logging into GitHub requires their own browser.
Tell them to run:
```
gh auth login
```
and answer the prompts:
- "What account do you want to log into?" → **GitHub.com**
- "What is your preferred protocol?" → **HTTPS**
- "Authenticate Git with your GitHub credentials?" → **Yes**
- "How would you like to authenticate?" → **Login with a web browser**

It'll show a one-time code and open their browser — they paste the code in, approve
it, then come back and tell you it's done. Immediately after, run this yourself
(it's non-interactive, safe to run directly) so that later steps don't hit a
confusing "could not read username" error:
```bash
gh auth setup-git
```

**Vercel access**: there's no command-line check for this — just ask the human "are
you already able to log into vercel.com and see the project's team there?" If not,
they need someone with admin rights on that Vercel team to add them (by email), or
they need to create their own Vercel account and be invited.

Once through this section, continue to whichever of A/B/C/D they picked.

---

## How updates actually work (the big picture, in plain language)

Skip the jargon and explain it like this, once, so the human has a mental model
before diving into any of the four options:

> "The project's files live in two places: a copy on this computer (or whichever
> computer we're working from), and a copy on GitHub that Vercel watches. The cycle
> is always: **get the latest copy onto this computer → make changes → send the
> changes back up to GitHub → Vercel notices and automatically updates the live
> site within about a minute.** You never have to touch Vercel directly to publish
> a change — GitHub is the only handoff point."

**Getting the project onto a new/different computer** (only needed the first time on
a given machine, or a different one than before): find the GitHub repository URL
(ask the human, or check whichever chat/notes it was shared in), then:
```bash
git clone <repository-url>
cd <folder-name-it-created>
```
That downloads every file. From here on, "make changes → send them back up" (below)
is all that's needed — no need to re-clone each time.

**Sending changes back up**, after any edit (covered in detail per-option below):
```bash
git add -A
git commit -m "<a short plain-English description of what changed>"
git push
```
`git push` specifically is the one step that talks to the internet/GitHub, so if
your environment blocks or is cautious about network-touching commands run on the
human's behalf, this is the one to hand to them directly rather than run yourself —
tell them to paste it into their own terminal (or, in Claude Code specifically, type
`! git push` — the `!` runs it directly in their session). Everything before it
(`git add`, `git commit`) is safe to run yourself.

---

## A) Add new tasks to the dashboard

The human will paste one or more Mercor Studio task URLs, usually grouped like:

```
<Domain Name>
Full Tasks Set
Task 1 — <number> (<short description>): https://studio.mercor.com/admin/tasks/task_<hex>/?campaignId=...
Task 2 — <number> (<short description>): https://studio.mercor.com/admin/tasks/task_<hex>/?campaignId=...

Prompts Only Set
Prompt 1 — <number>: https://studio.mercor.com/admin/tasks/task_<hex>/?campaignId=...
Prompt 2 — <number>: ...
Prompt 3 — <number>: ...
```

If they haven't pasted anything yet, ask them to paste the Studio link(s) and tell
you which domain each belongs to.

Full tasks: up to 2 per domain, each becomes a complete card (prompt, rubric, real
downloadable files). Prompt-only entries: up to 3 per domain, lightweight cards
labeled "Prompt example N · Task `<number>`", prompt text only, no rubric/files.

Process one URL at a time, fully, before moving to the next — fetch → extract →
verify → splice → validate. Don't batch-fetch several tasks and extract later.

### A1 — Open the task page

If your environment has browser automation available (Claude in Chrome, a
Playwright-style MCP tool, or similar), use it to navigate to the URL. If it
doesn't, ask the human to open the link themselves and tell them exactly what
you need them to do next (see A2).

Wait ~7 seconds after navigating, then check the page actually loaded real content
(e.g. `document.body.innerText.length` via whatever JS-execution tool is available).

**The Studio blank-page quirk** (recurs often): the page can render with zero text
even after multiple wait/reload cycles. When this happens: reload once, wait again,
recheck. If still blank after 2 attempts, tell the human plainly ("Studio is showing
a blank page for this task after two tries — could you check it in your own browser
and let me know when to retry?") and wait — don't loop silently.

### A2 — Get the exact, full raw text (never type it out by hand)

Never paraphrase or hand-transcribe prompt/rubric text from a preview — it will
silently introduce errors (e.g. curly vs. straight quotes). Get the *exact* text via
a Blob download:

```js
window.__mainText = document.body.innerText;
const blob = new Blob([window.__mainText], {type: 'text/plain'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = '<name>_full.txt';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
window.__mainText.slice(0, 400); // sanity check: confirms the task number/title
```

If you have a JS-execution tool for the browser, run this yourself. If you don't,
tell the human: "Please open your browser's developer console on that page (usually
F12 or right-click → Inspect → Console), paste in this code, press Enter, then tell
me once the file has downloaded" — and give them the snippet above.

Read the returned first-400-chars slice and confirm it shows the **expected task
number** before trusting the download — Studio can silently load the wrong task if
navigation didn't fully settle.

**Downloads duplicate-suffix gotcha**: if an earlier blank-page attempt already
triggered a 0-byte download with the same filename, the browser silently renames the
new successful download to `<name> (1).txt`. Always check both:
```bash
find ~/Downloads -maxdepth 1 -iname "<name>*" -exec wc -c {} \;
```
and move the correctly-sized file — never blindly assume the base filename is right.

**Never delete anything from the human's Downloads folder without asking first** —
including zips you just extracted yourself this session.

### A3 — Extract the exact prompt text (boundary markers)

The prompt lives between `User\n` and the **earliest-occurring** of these markers
(check all of them — which one comes first varies task to task, and new ones can
turn up):

```python
text = open('<name>_full.txt', encoding='utf-8').read()
start = text.find('User\n') + len('User\n')
candidates = {
    'PII': text.find('\nPII', start),
    'Prompt-Rubric Alignment': text.find('\nPrompt-Rubric Alignment', start),
    'Prompt-Rubric alignment (lower quality)': text.find('\nPrompt-Rubric alignment (lower quality', start),
    'Admin only Prompt Check': text.find('\n[Admin only] Prompt Check', start),
    'Trajectory complexity guidance': text.find('\nTrajectory complexity guidance', start),
}
end = min(v for v in candidates.values() if v != -1)
```

`Trajectory complexity guidance` (an AI-generated "how to increase difficulty"
admin note) can appear **before** `Prompt-Rubric Alignment` — always compute all
candidates and take the minimum, never assume a fixed marker or fixed order.

**Before trusting the boundary**, print ~150 chars of context around it and confirm
the text just before it reads like a natural end-of-prompt sentence, not mid-narrative
(a false-positive substring match is a real risk with common words like "PII").

Then extract and clean:
```python
prompt = text[start:end].rstrip('​').rstrip()
open('<name>_prompt.txt', 'w', encoding='utf-8').write(prompt)
```

Check for characters that will need escaping later:
```bash
grep -c '`' <name>_prompt.txt
grep -c '${' <name>_prompt.txt
```
A non-zero count isn't an error — confirm it's genuine source content, then make
sure the JS-embedding step (A6) escapes it.

Prompt-only cards stop here — build the object (A6, prompt-only variant) and splice
it in.

### A4 — For full tasks: extract the rubric

1. Locate the rubric block: from `"Task Rubric\n"` to `"Add rubric item"`.
2. Wrap the raw text as `[{"type": "text", "text": <full_text>}]` and save as
   `<name>_dump.json` — this is the input format `scripts/parse_rubric.py` (shipped
   alongside this skill) expects.
3. Run:
   ```bash
   python3 <path-to-this-skill>/scripts/parse_rubric.py <name>_dump.json > <name>_rubric.json
   ```

The parser handles:
- Two distinct raw layouts Studio can emit for the same table: columns separated by
  literal tab-only lines, or columns separated by plain blank lines — it
  auto-detects per row.
- `Balboa Rubric` rows (free-text description/rationale/type/tags/weight) and
  structured `Content length` / `Page count` programmatic-verifier rows.
- Annotator-view quirks: a badge line between the marker and description,
  comma-joined tags, and quality-check narrative bleeding into the weight field.

**Known irreducible gaps** — the parser cannot recover these; inspect the Studio UI
directly (switch **Structured ↔ Spreadsheet** view, reveal hidden columns via the
**Columns** button) and hand-correct the JSON:
- An all-dash stub row where the real target file/metric/min/max/weight only exist
  as actual form values, not text.
- A `weight` that comes back as leaked narrative (`"Results may be stale"`,
  `"Convert to Images"`, `"Rubric Check"`) instead of a number.
- Tags containing `[object Object]` fragments — clean by keeping only tokens
  matching the known vocabulary (`Reasoning`, `Extraction`, `Style`).

After any hand-fix, or after changing the parser, **regression-test against every
previously-successful task's `_dump.json`** before trusting new output.

### A5 — Metadata and files

**Metadata** (`Domain`, `Prompt File(s) Count`, `Solution File Type`, `Set`,
`Expected Peer Difficulty Level`) does **not** appear in the text dump — these are
form-field widgets, not plain text. Get these by scrolling to that section and
reading a screenshot (or asking the human to read them off the page to you, if you
have no screenshot tool available).

**Files** (input + golden-response) show up in one of these shapes:
1. A direct per-file download icon on hover/click.
2. A bulk "Download Filesystem" button — downloads a zip; unzip, copy contents into
   `files/<task-id>/`, then remove the temp zip (ask before deleting from Downloads).
3. A new tab with a signed, time-limited URL — download it (e.g. `curl`) **within 5
   minutes** of it appearing, then close the tab.
4. A preview modal with a Download button inside — click through the modal first.

Verify every downloaded file with `file <path>` (confirms it's a real, non-corrupt
document, not an HTML error page saved with the wrong extension).

### A6 — Build the entry and add it to the site

Two escape rules, used consistently everywhere text gets embedded into `data.js`:
- Backtick-quoted fields (`prompt`, `promptText`): escape backslashes, backticks, and
  `${`.
- Double-quoted fields (rubric `description`/`rationale`/tags): escape backslashes,
  double-quotes, and turn real newlines into the two-character sequence `\n`.

Full-task shape:
```js
{
  id: "<domainabbrev>-task-<number>",
  taskName: "Task <number> — <Title>",
  domain: "<Domain Name>",
  promptFileCount: "<e.g. 2-3>",
  solutionFileType: "<e.g. Spreadsheets>",
  set: "<A|B>",
  expectedPeerDifficulty: "<e.g. <6 hours>",
  prompt:
`<escaped prompt text>`,
  inputFiles: [ { name: "<file>", url: "files/<domainabbrev>-task-<number>/<file>" } ],
  goldenResponse: [ { name: "<file>", url: "files/<domainabbrev>-task-<number>/<file>" } ],
  rubric: [
    { index: <n>, description: "<escaped>", rationale: "<escaped>", type: "<type>", tags: [<tags>], weight: <number or "—"> },
  ],
},
```
Prompt-only shape:
```js
{ id: "<domainabbrev>-prompt-<number>", taskName: "<number>", promptText:
`<escaped prompt text>`, },
```

Splice into `data.js`'s `REAL_TASKS`/`REAL_PROMPTS` objects, keyed by domain name —
insert into a brand-new domain's array right after it's created, or append to an
existing domain's array without disturbing what's already there (read that domain's
current array first).

Then validate and preview (see **"After any change — always check your work"**
below) before moving to the next URL.

---

## B) Change how the dashboard looks

Everything visual lives in one file, `index.html` — no build step, no separate CSS
file. Ask what specifically they want changed, or if they just said "make it look
better," **offer 3-6 concrete named options with a one-line description each and
wait for them to pick** before changing anything — never redesign silently.

Where things live in `index.html`:
- A `:root { ... }` block near the top holds every color as a named variable
  (background, text, accent colors, font choices) — most visual changes are edits
  here.
- A handful of `render...` functions build the actual page content.
- grep for hardcoded color codes (`#` followed by 3 or 6 letters/numbers) outside
  that `:root` block — things like a logo or favicon sometimes hardcode a color that
  needs updating in step with the rest of the palette.

If real brand colors or a real logo are requested and you don't have the exact
values/asset, **ask for them** rather than guessing — this represents a real
organization's identity, not a generic placeholder.

After any edit, see **"After any change — always check your work"** below.

---

## C) Fix or update something already on the site

This is the lightweight version of A — same accuracy rules, smaller scope.

1. Find the exact place in `data.js` — search for the task's ID, title, or a
   distinctive phrase from the text being fixed.
2. If the fix is correcting a typo or copy error: re-check it against the original
   Studio source (re-open the task, extract fresh text as in A2/A3) rather than
   guessing at the "obviously correct" wording — the whole point of this project is
   word-for-word accuracy, so even a fix should be sourced, not assumed.
3. Make the smallest edit that fixes the issue — don't rewrite surrounding content
   that wasn't asked about.
4. See **"After any change — always check your work"** below.

If asked to verify the whole site's content is accurate (not just fix one reported
issue): for every full task, pull its `prompt` and every rubric row's
`description`/`rationale` back out of `data.js`, reverse the escaping, and compare
byte-for-byte against the saved raw source file from when it was first added. Any
real mismatch found this way likely means a systematic bug (not a one-off typo) —
fix it once, then recheck *every* task that could be affected, not just the one
reported. A task with no saved raw source can't be checked this rigorously — say so
plainly rather than claiming full confidence.

---

## D) Publish your changes online (deploy)

Make sure **"Getting your accounts and tools ready"** (above) has been done first.

### First time ever deploying this project

```bash
git init
git add index.html data.js files/
printf 'scratch/\n.DS_Store\n' > .gitignore
git add .gitignore
git commit -m "Initial commit"
```
All local, safe to run directly. Then create an empty repository on github.com
(or ask the human to — a private repo is a reasonable default unless they say
otherwise), and:
```bash
git remote add origin <repository-url>
```
Then hand the actual push to the human (see "How updates actually work" above for
why) — have them run `git push -u origin main` themselves (via their own terminal,
or by typing `! git push -u origin main` if working in Claude Code).

Then link it to Vercel — through the dashboard is the most reliable path regardless
of environment:
1. vercel.com → confirm the correct **team** is selected (top-left switcher).
2. **Add New… → Project** → select the GitHub repo.
   - If it's not listed / an error mentions installing the GitHub integration: go to
     **github.com/apps/vercel** → Configure → grant repository access to that repo →
     save → refresh the Vercel import page.
3. **Project Name** field: must be **lowercase**, only letters/digits/`.`/`_`/`-`, no
   `---` in a row.
4. Framework preset: **Other**. Leave build command/output directory/root directory
   as default — this is a static site, no build step.
5. Deploy.

### Every time after that

```bash
git add -A
git commit -m "<short description of the change>"
```
(safe to run yourself), then the human runs `git push` themselves. Because the
project is linked to Vercel via GitHub, that push alone triggers a new live
deployment automatically within about a minute — no separate Vercel step needed.

### Sharing the link

The first deploy usually gives a **preview** URL (has a random-looking string in
it). The stable **production** URL (no random string) is on the project's Overview
tab under **Domains** — that's the one worth sharing long-term.

A team project with company single-sign-on enabled will, by default, require
*anyone* visiting the link to log into that Vercel team first. To make it viewable
by anyone with the link instead (no login), set up **Password Protection** in the
dashboard: Project → Settings → Deployment Protection (this is a paid-plan feature —
if it's greyed out, the team's current plan doesn't include it).

---

## After any change — always check your work

Regardless of which option (A/B/C/D) was used:

1. Validate `data.js` if it was touched:
   ```bash
   node --check data.js
   grep -c "PLACEHOLDER" data.js   # must print 0
   ```
2. Validate `index.html`'s script if it was touched (extract the `<script>...</script>`
   body to a temp `.js` file first, since `node --check` can't check an HTML file
   directly), then `node --check` that.
3. Restart the local preview so changes actually show up:
   ```bash
   pkill -f "http.server 8743"
   python3 -m http.server 8743   # run from the project's root folder
   ```
4. Check every new file link actually works:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8743/files/<task-id>/<file>
   ```
   — must print `200`.
5. Open it in a browser and **hard-reload** (a plain refresh can show a stale
   cached copy) — visually confirm the change looks right before telling the human
   it's done.

---

## Edge cases

| Situation | Action |
|---|---|
| Studio page renders blank after 2 reload attempts | Tell the human plainly, wait for "retry"; don't loop silently |
| Multiple prompt boundary-marker candidates found | Always take the **earliest** — never assume a fixed marker or order |
| Rubric row description spans several blank-line-separated paragraphs | The parser must find the true column boundary via the tab-only separator line, not the first blank line |
| Weight/description comes back as leaked UI narrative | Inspect Studio's Structured/Spreadsheet view + hidden columns directly, hand-correct |
| Signed file URL in a new tab | Download it within the ~5-minute expiry, immediately |
| A file already exists 0-byte in Downloads from an earlier attempt | Retry produces `<name> (1).ext` — glob-match, pick the correctly-sized file |
| Need to delete anything from the human's Downloads folder | Ask first, every time |
| `git push` / creating a GitHub repo / any action that touches the network | Prefer to hand this to the human to run themselves, especially if your environment restricts or flags network-touching commands |
| Vercel API reports a project created but you then can't see/manage it | A team-level permission wall, not a bug — switch to the dashboard-driven import |
| Project name rejected on Vercel import | Must be lowercase, no `---` — fix the Project Name field, not the repo name |
| Brand colors/logo requested but exact values not given | Ask for them rather than guessing at a real organization's identity |
| Task has no saved raw source for verification | Say so explicitly; don't claim the same accuracy guarantee as tasks that do |
| Working in an environment with no browser automation or no shell access | Ask the human to do that one physical step (open the link, paste a console snippet, run a command) and tell you the result, then continue |

---

## Constants

| Constant | Value |
|---|---|
| Preview server | `python3 -m http.server 8743` from the project's root folder |
| Rubric block markers | start `"Task Rubric\n"`, end `"Add rubric item"` |
| Prompt-only card label format | `"Prompt example N · Task <number>"` |
| Full-task rubric row fields | `index, description, rationale, type, tags, weight` |
| Rubric `type` values | `Critical`, `Nice-to-have`, `Subjective`, `Style / Formatting`, `Programmatic` |
| Known rubric tag vocabulary | `Reasoning`, `Extraction`, `Style` |
| Boundary-marker candidates (prompt end) | `\nPII`, `\nPrompt-Rubric Alignment`, `\nPrompt-Rubric alignment (lower quality`, `\n[Admin only] Prompt Check`, `\nTrajectory complexity guidance` |
| Signed file URL expiry | ~5 minutes |
| Vercel project name rules | lowercase; letters, digits, `.`, `_`, `-`; no `---`; ≤100 chars |
