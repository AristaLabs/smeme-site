# Homepage demo videos: plan

Two videos fill the "Demo coming soon" frames in the homepage demos section
(`src/templates/landing/preview.html`, `#demo-run` and `#demo-build`).

Real product on production, captions on, no voiceover, 16:9 (the `.v4-video`
frame). Each video walks the prompts printed directly beneath it, in the same
order and with the same wording, so a viewer can pause and copy.

Governing decisions: @smeme-cloud/docs/campaign/gtm/SMEme_GTM_Plan.md §1
(oversight split), §6 (claims boundaries, terminology), §8 (website demos).

## Demo A · Run a decision tree (1:00–1:15)

Frame caption: "A real run: the ACME withholding matter in Claude."

Tree: the opt-in ACME example (`U.S. Withholding on Cross-Border Payments to
Foreign Businesses`), loaded from `/decision-trees/acme-langgraph-example` in
the demo account. Evidence: the matter-123 files from the synthetic case bundle
(`smeme-acme-dataset-distributed.zip`), attached to a Claude Project. The
fictional-matter disclaimer must be visible at least once on screen.

Conclusions the tree can reach (from the fixture): No Withholding Required ·
Withhold at Reduced Treaty Rate · Withhold at Statutory 30% · Backup
Withholding Applies (24%) · Special-Regime Withholding Applies · Escalate to
Tax Counsel.

| # | On screen | Page prompt | Expected result |
|---|---|---|---|
| 1 | Paste prompt 1 in a new Claude chat | "Which SMEme decision trees do I have deployed? …" | Claude lists the ACME tree with its one-line description |
| 2 | Paste prompt 2; agreement and W-8BEN-E visible in the Project | "Run my cross-border withholding SMEme decision tree on this case: the ACME royalty to Party D …" | Claude gathers answers from the files, cites a source per answer, asks when it can't find one, returns **Withhold at Reduced Treaty Rate** and names the deciding answers |
| 3 | Paste prompt 3 | "Same case, but suppose Party D's W-8BEN-E had expired before the payment date …" | **Withhold at Statutory 30%**, with the difference from baseline |
| 4 | Paste prompt 4 | "What's the smallest change in the facts that would get this matter to **No Withholding Required**? …" | The facts that would have to change and the evidence each would need |

Cut between prompts; keep the tool-call indicator visible when Claude calls
SMEme. Hold on the result in steps 2 and 4.

Step 4 target: the page prompt currently says "[the reduced treaty rate]", which
is the baseline outcome. Change it to "No Withholding Required" (step 1 below).

## Demo B · Build a decision tree (1:15–1:30)

Frame caption: "Build your first decision process."

Procedure: client acceptance (new-client intake and conflicts), per the GTM
decision of 2026-10-24. The page's bracketed example "approving a new vendor"
is a placeholder; the video shows what the user typed in its place.

| # | On screen | Page prompt | Expected result |
|---|---|---|---|
| 1 | Paste the Connect prompt in Claude; sign-in tab opens; sign in; back to chat | "Connect me to SMEme over MCP. The instructions are at smeme.ai …" | Claude confirms it can see SMEme's tools |
| 2 | Paste the Build prompt with "client acceptance" filled in; answer the interview briefly | "Build a SMEme decision tree for a decision I sign off on repeatedly: …" | Three approval stops, each shown and approved: outcomes → questions → full outline. Claude saves the draft and says how to Deploy |
| 3 | Paste the Deploy prompt; follow it in the SMEme editor | "My SMEme draft is saved. Walk me through Deploy and switching Listed on …" | Deploy, then Listed on; tree shows Live |
| 4 | New chat; run it on a case with a known answer (the page's own "then start a new chat" instruction) | A one-line run prompt in the style of Demo A step 2 | Report with the outcome and deciding facts |

The interview in step 2 is the long part. Record it in full, then cut to the
three approval stops and one or two interview exchanges. Keep every on-screen
answer short enough to read in a caption.

## Synthetic data

**Demo A** uses the existing ACME bundle, `smeme-acme-dataset-distributed.zip`
(v`0.2.0-phase2-partial`, SHA-256
`96b8534209b11ca64899be4f054077ca6000ead1059437cd6343968554add560`), kept in
`smeme-cloud/smeme/landing/artifacts/` and mirrored at `src/downloads/`.
Eight fictional matters, `matter-123` … `matter-130`; every document carries a
source ID and the synthetic notice. `matter-123` is the clean treaty-rate case
(agreement extract, intake memo, Sept 11 email, CRM and register records,
royalty schedule, W-8BEN-E extracted-fields JSON). `matter-129` has a
change-in-circumstances notice if a second case is ever needed.

- The bundle ships no answer key, option strings, or question text. Expected
  results come from the dry run (step 4), not from the dataset.
- The W-8BEN-E is extracted-field JSON, not a form image, by design. Do not
  fabricate a form for the camera; let captions name the files.
- The dataset README states the tax content is not reviewed by qualified tax
  counsel and should not be presented to prospects as a realistic legal
  artifact until it is. Resolve before publishing: a practitioner review, or a
  notice revision that matches the label-only posture. Recorded under Open
  decisions.

**Demo B** has no dataset yet. Build one small set for a fictional firm:

1. A one-to-two page procedure, "New Client Acceptance and Conflicts," to
   attach in prompt 2. Outcomes (Accept · Accept with escalation · Decline ·
   Escalate to ethics partner), the questions a partner actually asks
   (conflicts search, matter within practice scope, source of funds,
   sanctions/PEP, engagement terms, capacity), two named edge cases.
2. Two or three past matters with known outcomes, each a short intake form
   and an email thread, for the "bring past cases" step. One goes the less
   obvious way. These become the Deploy-time test cases.
3. One fresh matter for the new-chat run in step 4.

Same hygiene as ACME: source IDs in frontmatter, `.invalid` mail domains, the
synthetic notice on every file, no resemblance to a real firm or client, and a
caveat that it is a model procedure, not a bar-reviewed one.

## Pre-production

1. **Serial.** Fix the Demo A step 4 prompt target in `preview.html`
   (`#lp-prompt-reach`): "[the reduced treaty rate]" → "No Withholding
   Required". Run `pytest tests/test_build.py`.
2. **Serial, after 1.** Commit the pending site redesign so the frames and
   prompts the videos reference are fixed. Ship it with the "Demo coming soon"
   frames; the videos replace them later.
3. **Parallel with 2.** Create the demo account on production (free tier: the
   ACME tree and the client-acceptance tree use two of three slots). Load the
   ACME example and download the case bundle. Create a Claude Project
   containing only the matter-123 files Demo A needs (agreement, W-8BEN-E,
   intake memo, email).
4. **Parallel with 2.** Dry-run Demo A end to end in Claude against production.
   Record exactly what Claude shows during `evaluate` / `evaluate_continue`:
   whether each answer is presented with a source ID before SMEme evaluates, how
   many answers decide the outcome, and how the what-if and how-to-reach
   results read. Adjust the expected-result column above to what actually
   appears; do not script what the product does not show.
5. **Parallel with 2, before 5a.** Write the Demo B synthetic set (see
   Synthetic data). Keep it under `smeme-site/src/downloads/` beside the ACME
   bundle only if it is meant to be public; otherwise outside the repos.
5a. **Serial, after 5.** Dry-run Demo B end to end, unassisted, in a fresh chat.
   Time it. Log where it stalls (OAuth, empty account, interview length,
   Deploy/Listed, first run) in the activation friction log,
   @smeme-cloud/docs/campaign/gtm/workflow-builders/market-workflow-builders.md
   §12.5. Decide which interview exchanges to keep.
6. **Serial, after 4 and 5a.** Freeze the two shot tables above. If a dry run
   contradicts a prompt on the page, fix the page, not the video.

## Recording and post

7. **Serial, after 6.** Record both demos in one session on the same account.
   Clean browser profile, no bookmarks bar, Claude at a width that keeps the
   tool-call indicator readable. Capture at 1920×1080 or larger.
8. **Serial, after 7.** Edit: cuts between prompts, captions for every typed
   prompt and every result, fictional-matter label on screen in Demo A, no
   "deterministic" in any caption (use "same facts, same result" if the point
   comes up). If "Rational AI" appears in a title card, define it in the same
   card. Export 16:9 MP4 with a poster frame on the result card.
9. **Parallel with 8.** Decide hosting: self-hosted MP4 in the static build vs.
   an embed. Self-hosted keeps the page free of third-party scripts; check the
   build output size and `build.py` asset handling before choosing.
10. **Serial, after 8 and 9.** Replace the two `figure.v4-video` placeholders
    in `preview.html` with the players; update `tests/test_build.py`
    expectations that assert on "Demo coming soon"; commit and deploy.
11. **Serial, after 10.** Update
    @smeme-cloud/docs/campaign/gtm/SMEme_GTM_Plan.md: §8 shot-list pointer to
    this file, §15 "Website demos produced to shot list", and the Preparation
    row in §13. This clears the gate for Shapiro and Cole Medin outreach.

## Claims boundaries carried into the videos

- Fictional matter and fictional procedure; nothing shown is legal or tax
  advice. Label on screen, not only in the page note.
- The agent proposes answers; the user admits them; SMEme determines what
  follows. Do not cut the admission so that SMEme appears to read the files.
- Review is smaller and better located, not removed. Demo A step 2 should
  show Claude asking the user for at least one answer it could not find.

## Open decisions

- Demo B procedure: client acceptance (recommended, matches the GTM decision)
  or change the page placeholder to match whatever is recorded.
- Hosting (step 9).
- ACME substantive-review caveat: practitioner review before publishing, or
  revise the dataset notice to the label-only posture.
- Whether the ACME maintainer archive (regression answers) still exists
  outside the repos; it would shortcut step 4.
