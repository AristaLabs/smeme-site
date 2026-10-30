# Homepage demo videos: production plan

Version: 1.0 | Finalized October 28, 2026 | Owner: Dan Arista

Status: ready to produce. The site work the videos depend on is live
(generic sample prompts, redesign committed, `/builders` and `/docs/langgraph`
retired). What remains is account setup, the Demo B data set, two dry runs,
recording, and post.

Two videos fill the two "Demo coming soon" frames in the homepage demos
section (`src/templates/landing/preview.html`, `#demo-run` and
`#demo-build`). There is no third frame; `/builders` redirects to `/docs`.

Real product on production, captions on, no voiceover, 16:9 (the `.v4-video`
frame). These are demos, not how-to videos. A viewer watches a run and a
build on our account. They do not need the ACME files, and they are not
asked to paste the lines said on screen.

The copyable prompts on the page are generic sample prompts for the harness
the visitor already uses. They are specified in
@smeme-cloud/docs/campaign/gtm/canonical-example-brief.md and are not the
script below. If a dry run contradicts the script, fix the script here;
leave the page prompts alone.

Governing decisions: @smeme-cloud/docs/campaign/gtm/SMEme_GTM_Plan.md §1
(oversight split), §6 (claims boundaries, terminology), §8 (website demos).
Recording notes for the ACME matter live in the canonical-example brief; if
the fixture changes, update the brief first, then this file.

## Demo A · Run a decision tree (1:00–1:15)

Frame caption: "A real run: the ACME withholding matter in Claude."

Tree: the opt-in ACME example (`U.S. Withholding on Cross-Border Payments to
Foreign Businesses`), loaded from `/decision-trees/acme-langgraph-example` in
the demo account. Evidence: the matter-123 files from the synthetic case
bundle, attached to the chat (a Claude Project holding only those files is
the simplest way to keep them attached across takes). The fictional-matter
disclaimer must be visible at least once on screen.

Conclusions the tree can reach (from the fixture): No Withholding Required ·
Withhold at Reduced Treaty Rate · Withhold at Statutory 30% · Backup
Withholding Applies (24%) · Special-Regime Withholding Applies · Escalate to
Tax Counsel.

| # | On screen | Said in the demo (recording script) | Expected result |
|---|---|---|---|
| 1 | New Claude chat | "Which SMEme decision trees do I have deployed? Give me the name and a one-line description of each." | Dry run 2026-10-29: Claude listed the ACME tree ("Works out whether, and at what rate, U.S. withholding applies when a U.S. payer pays a foreign business") and a second deployed tree, CFIUS Mandatory Declaration (31 CFR 800.401). Hide or remove the CFIUS tree before recording so this shot shows only the withholding tree. |
| 2 | Agreement, W-8BEN-E, intake memo, and email attached | "Run my cross-border withholding SMEme decision tree on this case: ACME's Q3 royalty to Party D, matter 123. First list the other apps and connectors you can already read. Then use only the attached files. Gather the evidence, cite where each answer came from, and ask me when you can't find one. Then tell me the outcome and which answers decided it." | Dry run 2026-10-29. Claude cited sources for the file-backed answers, then asked the user twice: q6 (**Not a chapter 4 withholdable payment**) and the "treaty in force" part of q8 (**Yes: treaty in force, residence certified, limitation-on-benefits provision identified, and article/rate stated**). q9 was **No red flags**. Outcome: **Withhold at Reduced Treaty Rate**. Decisive support: all nine answers. Run `fb288dcc-386f-4d32-ab2e-f6406b4b30e3`. Claude also suggested depositing tax and filing Forms 1042 and 1042-S; do not caption that as a SMEme result. |
| 3 | Same chat | "Same case, but suppose Party D's W-8BEN-E had expired before the payment date. Does the outcome change? Show me what's different from the baseline." | Dry run 2026-10-29. **Withhold at Statutory 30%.** Only q7 changes, from "Yes, valid and current" to "No, expired, incomplete, or not on file." The path ends at q7 (7 questions); q8 and q9 are not reached. Do not run Claude's offered q1 "undocumented" variant, which it said could reach backup withholding. Do not caption the Form 1042 advice as a SMEme result. |
| 4 | Same chat | "What's the smallest change in the facts that would get this matter to No Withholding Required? List each fact that would have to change and what evidence would support it." | Dry run 2026-10-29. Three one-change routes, each enough on its own: (1) payee is a U.S. person with a valid W-9, (2) platform used solely outside the United States, (3) income effectively connected and a valid W-8ECI on file. The current files contradict all three. Do not show SMEme's preview excerpts for the changed answers; the dry run found they still carry the baseline evidence. Do not caption Claude's note that route 3 moves the payee onto a U.S. return. |

Cut between asks; keep the tool-call indicator visible when Claude calls
SMEme. Hold on the result in steps 2 and 4. Step 4 asks for No Withholding
Required because the treaty rate is the baseline.

Dry run 2026-10-29, done:

- Claude showed each file-backed answer with its source before the outcome,
  and stopped to ask the user twice: q6, and the "treaty in force" part of q8.
- Decisive support named all nine answers.
- What-if and how-to-reach wording is in rows 3 and 4.

## Demo B · Build a decision tree (1:15–1:30)

Frame caption: "Build your first decision process."

Procedure: client acceptance (new-client intake and conflicts), per the GTM
decision of 2026-10-24. The recording fills that name in; the page's sample
build prompt keeps its own placeholder for the visitor.

| # | On screen | Said in the demo (recording script) | Expected result |
|---|---|---|---|
| 1 | Claude; sign-in tab opens; sign in; back to chat | "Connect me to SMEme over MCP. The instructions are at smeme.ai. Walk me through adding it as a connector in this app, step by step. When the sign-in tab opens I'll sign in and come back. Then confirm you can see SMEme's tools." | Claude confirms it can see SMEme's tools |
| 2 | Procedure document attached; answer the interview briefly | "Build a SMEme decision tree for a decision I sign off on repeatedly: accepting a new client. The firm's procedure is attached. Load SMEme's design guidance and follow it. Interview me, then stop for my approval three times: the outcomes, the questions, then the full outline. Ask me where the answer to each question comes from. When I approve, save it as a draft and tell me how to Deploy it." | Dry run 2026-10-29. Quick encode, three stops. Unsure escalates on every question. Terms stay before capacity. Draft saved, not deployed: **New Client Acceptance and Conflicts (HP-07)**, `67873061-7fac-463e-869a-c69f0497a4c1`, 18 test cases including Marlowe → Accept and Ostrander → Escalate to ethics partner. |
| 3 | SMEme editor | "My SMEme draft is saved. Walk me through Deploy and switching Listed on in the SMEme editor, step by step." | Dry run 2026-10-29. Deploy passed 18 test cases. Editor shows v1, **Live**, Listed, structurally valid. |
| 4 | New chat, not the build chat. Attach only the Quillfeather intake form and email. | "Run my client acceptance SMEme decision tree on this new matter. Use only the attached intake form and emails. Cite where each answer came from, and ask me when you can't find one. Then tell me the outcome and which answers decided it." | Dry run 2026-10-29. Claude asked one question: engagement terms. Answer **Not yet agreed** (the Oct 26 email approves the fee only; the partner has not signed). Outcome: **Accept with escalation.** That one answer decided it. Capacity was not asked. Run `a2ff447d-cb58-4020-88b4-a45f37a6504b`. |

The interview in step 2 is the long part. Record it in full, then cut to the
three approval stops and one or two interview exchanges. Keep every
on-screen answer short enough to read in a caption. If past matters are
offered as test cases during the interview, show the Deploy-time test run in
step 3.

## Synthetic data

**Demo A** uses the existing ACME bundle, `smeme-acme-dataset-distributed.zip`
(v`0.2.0-phase2-partial`, SHA-256
`96b8534209b11ca64899be4f054077ca6000ead1059437cd6343968554add560`), kept in
`smeme-cloud/smeme/landing/artifacts/` and mirrored at `src/downloads/`
(copied to `public/downloads/` by `build.py`). Eight fictional matters,
`matter-123` … `matter-130`; every document carries a source ID and the
synthetic notice. `matter-123` is the clean treaty-rate case: agreement
extract, intake memo (draft 2), Sept 11 email, CRM and register records,
royalty schedule, W-8BEN-E extracted-fields JSON. Attach to the demo chat:
`agreement/asset-x-agreement-extract.md`, `tax/w8bene-extracted-fields.json`,
`drive/intake-memorandum.md`, `email/2026-09-11-correspondence.eml`.
`matter-129` has a change-in-circumstances notice if a second case is ever
needed.

- The bundle ships no answer key, option strings, or question text. Expected
  results come from the dry run, not from the dataset.
- The W-8BEN-E is extracted-field JSON, not a form image, by design. Do not
  fabricate a form for the camera; let captions name the files.
- The public zip path stays:
  `https://smeme.ai/downloads/smeme-acme-dataset-distributed.zip`, copied from
  `src/downloads/` by `build.py`. The video does not point viewers at it.
- The dataset README says the tax content has not been reviewed by qualified
  tax counsel. Publishing does not wait on that review. The video opens with
  a fictional-matter label, and a note sits under the video on the page
  (decision, 2026-10-28).

**Demo B** needs a small set for a fictional firm, written before its dry run:

1. A one-to-two page procedure, "New Client Acceptance and Conflicts," to
   attach in step 2. Outcomes (Accept · Accept with escalation · Decline ·
   Escalate to ethics partner), the questions a partner actually asks
   (conflicts search, matter within practice scope, source of funds,
   sanctions/PEP, engagement terms, capacity), two named edge cases.
2. Two or three past matters with known outcomes, each a short intake form
   and an email thread, offered as test cases during the interview. One goes
   the less obvious way.
3. One fresh matter (intake form plus one or two emails) for the step 4 run.

Same hygiene as ACME: source IDs in frontmatter, `.invalid` mail domains, the
synthetic notice on every file, no resemblance to a real firm or client, and
a caveat that it is a model procedure, not a bar-reviewed one. Keep the set
outside the repos unless it is meant to be public; if public, it goes under
`src/downloads/` beside the ACME bundle.

## Pre-production

1. **Parallel.** Create the demo account on production (free tier: the ACME
   tree and the client-acceptance tree use two of three slots). Load the
   ACME example from `/decision-trees/acme-langgraph-example`; download the
   bundle; create a Claude Project with the four matter-123 files above.
2. **Parallel.** Write the Demo B synthetic set.
3. **Serial, after 1.** Dry-run Demo A on production. Work the dry-run
   checklist; rewrite the expected-result column to what appears. Do not
   script what the product does not show.
4. **Serial, after 2.** Dry-run Demo B end to end, unassisted, in a fresh
   chat. Time it. Log where it stalls (OAuth, empty account, interview
   length, Deploy/Listed, first run) in
   @smeme-cloud/docs/campaign/gtm/workflow-builders/market-workflow-builders.md
   §12.5. Decide which interview exchanges to keep.
5. **Serial, after 3 and 4.** Freeze both shot tables.

## Recording and post

6. **Serial, after 5.** Record both demos in one session on the same
   account. Clean browser profile, no bookmarks bar, Claude at a width that
   keeps the tool-call indicator readable. Capture at 1920×1080 or larger.
7. **Serial, after 6.** Edit: cuts between asks, captions for every ask and
   every result, fictional-matter label on screen in Demo A and a
   model-procedure label in Demo B, no "deterministic" in any caption (use
   "same facts, same result" if the point comes up). If "Rational AI"
   appears in a title card, define it in the same card. Export 16:9 MP4 with
   a poster frame on the result card.
8. **Parallel with 7.** Hosting. Default: self-hosted MP4 plus poster under
   `src/downloads/` or a new `src/media/`, copied by `build.py` the way the
   ACME zip is (see the `downloads` block around line 160). Keeps the page
   free of third-party scripts. Switch to an embed only if the two files
   push the static build past what the host serves comfortably.
9. **Serial, after 7 and 8.** Replace the two `figure.v4-video` placeholders
   in `preview.html` with `<video controls poster=…>` players and keep the
   figcaptions. `tests/test_build.py` does not assert on "Demo coming soon";
   add a test that both media files land in the build output. Commit and
   deploy.
10. **Serial, after 9.** Update
    @smeme-cloud/docs/campaign/gtm/SMEme_GTM_Plan.md: tick §15 "Website
    demos produced to shot list" and the Preparation row in §13. This
    clears the gate for Shapiro and similar practitioner outreach.

## Claims boundaries carried into the videos

- Fictional matter and model procedure; nothing shown is legal or tax
  advice. Demo A opens on that label. Demo B opens on a model-procedure
  label. Each video frame on the page has the same note directly under it.
  The use-case footer ("Fictional examples. Incomplete procedures. Not
  professional advice.") stays; it is not the note under the videos.
- The agent proposes answers; the user admits them; SMEme determines what
  follows. Do not cut the admission so that SMEme appears to read the files.
- Review is smaller and better located, not removed. Demo A step 2 shows
  Claude asking the user for at least one answer it could not find.
- Do not assign Backup Withholding or Special-Regime Withholding to any
  matter in the video, and do not say that changing any answer changes the
  result (brief, approved boundaries).

## Open decisions

- The ACME maintainer archive (regression answers) is not in any repo or git
  history. It is an answer key for the outcomes Demo A intends to show
  (treaty rate, then statutory 30% after an expired W-8). It does not
  produce those outcomes. Step 3 does: run the tree and record what comes
  back. If that matches the shot table, the archive is unnecessary. If it
  does not, change the shot table to the result the solver returns.
