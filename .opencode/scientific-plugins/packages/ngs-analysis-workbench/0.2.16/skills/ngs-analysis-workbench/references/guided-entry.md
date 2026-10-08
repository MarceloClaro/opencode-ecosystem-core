# Guided entry

Use this contract for open-ended onboarding, prompt discovery, walkthroughs,
and other requests that do not yet identify one concrete NGS task.

## Derive honest choices

Inspect authorized inputs and conversation context. Use live workflow catalogs
before offering a public example, but defer runtime inspection until the user
selects an outcome.

- If useful material exists, derive up to two distinct input-backed outcomes
  and add `Use a different input`.
- If no material exists and the user has not selected an entry mode, offer
  `Use my data` and `Try a public example`.
- If the user already requested a demo, inspect the bundled workflow
  configurations, intersect them with live bindings, and offer up to three
  outcome-level technical demonstrations.

Do not expose pipeline, engine, profile, compute target, runtime, or reference
choices at this entry point. Never invent an option to fill the list.

## Present one blocking decision

If two or three valid routes remain, call `request_user_input` with one concise
question and those routes.

If exactly one valid route remains, continue without asking. If the user has
already answered the decision, consume that answer instead of repeating the
question. A canceled or empty submission defers the flow.

Only when `request_user_input` is unavailable or fails before rendering,
present the same choices in chat. Never ask the user to paste another prompt.

## Continue the selected route

- For `Use my data`, ask for the smallest useful accessible path, manifest,
  metadata file, or result identity, then follow `understand-ngs-data`.
- For an input-backed task, follow the focused skill implied by its scientific
  outcome.
- For a public demo, follow `run-ngs-analysis` as an explicitly limited engine
  or method demonstration unless the user states a scientific objective. Use
  the bundled workflow configuration when available.
- Treat free-form input as a concrete user-authored task and route it normally.

After selection, continue until the next real user decision, authorization
boundary, completed requested outcome, or evidence-backed blocker.
