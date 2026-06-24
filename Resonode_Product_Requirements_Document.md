# Product Requirements Document — Enterprise Communications Neuro‑Analyzer

**Working product name:** *Resonode* (provisional — confirm after trademark/domain clearance)
**Document type:** Consolidated Product Requirements Document (PRD) / build specification
**Prepared by:** [Big Four] Strategy Advisory, for [Startup Client]
**Intended consumer:** Development partner (AI‑native delivery on BMAD + Spec‑Kit)
**Version:** 1.0 (draft for development)
**Status:** Ready for spec ingestion — see Section 21 for items requiring client clarification

---

## How to use this document with BMAD / Spec‑Kit

This PRD is written to be consumed directly by a spec‑driven, AI‑assisted delivery pipeline.

- **As a BMAD PRD:** Sections 3–18 constitute the PRD body. The PM agent should treat Section 9 (Functional Requirements) as the epic/story source, Section 10 (Non‑Functional Requirements) as cross‑cutting constraints, and Section 18 (Release Plan) as the sharding/prioritisation order. The Architect agent should start from Section 8 (Architecture), Section 11 (Data Model) and Section 12 (Integrations).
- **As a Spec‑Kit `/specify` input:** Each Functional Requirement has a stable ID (`FR-Exx-n`), a single testable statement, and explicit **Acceptance Criteria**. Ambiguities are tagged inline as `[NEEDS CLARIFICATION: …]` and consolidated in Section 21 — resolve these before `/plan`.
- **Traceability:** Every FR maps to one or more backlog stories (`TCA-0xx`) from the competitive backlog workbook. IDs are stable; do not renumber.
- **Definition of Done** for any story is in Section 19 and applies globally unless a story states otherwise.

---

## 1. Document control

| Field | Value |
|---|---|
| Product (working) | Resonode — Enterprise Communications Neuro‑Analyzer |
| Owner | [Client product owner] |
| Delivery model | AI‑native (BMAD method + Spec‑Kit), partner‑built |
| Core engine | Open models, **TRIBE v2 primary**, others where better‑fit. **No in‑house model training.** |
| Target customers | Large IT‑services organisations (e.g. Sopra Steria, Capgemini, Accenture) |
| Phasing | Phase 1 Pilot/MVP → Phase 2 Scale → Phase 3 Advanced |

---

## 2. Executive summary

Resonode is an **analyser**: enterprise communications teams submit a communication artifact — an official communication, presentation, press release, internal communication, executive communication, training material, policy or similar collateral — and Resonode predicts **how the intended audience will respond** to it (attention, emotional response, comprehension, memorability, brand fit), highlights the weak parts, and recommends fixes, **before** the artifact is published or sent.

The product does this by **orchestrating existing open models** (primarily Meta FAIR's TRIBE v2, a tri‑modal model that predicts human brain/behavioural response to media) and mapping their raw output into actionable communication metrics. Resonode does **not** train its own foundation model. Its defensible value is the application layer: artifact rendering, the raw‑output‑to‑comms‑metric mapping and calibration, the enterprise workflow, and the governance/compliance/security envelope that consumer ad‑tech tools lack.

**Engineering artifacts (source code, configs, architecture/design docs) are explicitly out of scope.**

---

## 3. Goals and success metrics

### 3.1 Product goals
1. Give comms teams a **pre‑send, neuro‑grounded read** on any communication artifact within seconds (text) to minutes (multimodal).
2. Make the read **actionable** — pinpoint weak segments and recommend specific improvements.
3. Be **enterprise‑safe** for confidential internal/exec comms (data residency, no‑training guarantee, optional on‑prem).
4. Be **model‑agnostic** so the underlying model(s) can be swapped without re‑engineering the product.

### 3.2 Success metrics (measurable; target at GA)
| Metric | Target |
|---|---|
| Text‑only analysis latency (p95) | < 2 seconds |
| Full multimodal artifact analysis latency (p95) | < 60 seconds (deck/policy ≤ 50 pages) |
| Prediction validity vs human ground‑truth (attention) | ≥ 85% agreement on held‑out set `[NEEDS CLARIFICATION: client‑accepted accuracy threshold]` |
| Pilot client adoption | ≥ 60% of target comms team running ≥ 1 analysis/week within 8 weeks |
| Recommendation usefulness | ≥ 70% of surfaced recommendations rated "useful" by reviewers |
| Platform availability (Phase 2+) | ≥ 99.5% monthly |

---

## 4. Background and strategic context

- **TRIBE v2** is Meta FAIR's tri‑modal (video + audio + language) foundation model that predicts group‑average human brain (fMRI) responses to stimuli. It is the conceptual engine: render an artifact, run inference, obtain audience‑response signals — no human panels.
- **Licensing reality (critical constraint):** TRIBE v2 is released under **CC BY‑NC 4.0 (non‑commercial)**. Running production inference on TRIBE v2 inside a sold product is a commercial use. Resolution does not require building a model — see Section 13. The product must remain model‑agnostic so this can be honoured operationally.
- **Competitive whitespace:** neuro/attention vendors (Neurons, Realeyes, DAIVID, Dragonfly) predict well but are built for ads/consumer creative; enterprise content‑governance vendors (Acrolinx/Markup AI, Writer, VisibleThread) own the enterprise/compliance relationship but have no neuro‑prediction. Resonode targets the gap: neuro‑grounded analysis purpose‑built for internal/exec/policy comms with governance and compliance.

---

## 5. Scope

### 5.1 In scope
- Ingestion and analysis of communication artifacts: official communications, presentations/decks, press releases, internal communications, executive communications (incl. recorded town‑halls/videos), training materials, policies, and similar collateral.
- Predicted‑response metrics: attention, emotional response/tone, comprehension/cognitive load, memorability, brand/voice fit, clarity/readability, inclusivity, risk/compliance language.
- Recommendations, rewrite assistance (guardrailed), A/B comparison, benchmarking.
- Authoring integrations (Word, PowerPoint, Outlook, Teams), web app, API/SDK.
- Governance: brand/standards library, workflow/approval, analytics, model governance, security/compliance.

### 5.2 Out of scope
- **Engineering artifacts** — source code, configuration, infrastructure/architecture and design documents. The platform must detect and exclude these.
- **Training or fine‑tuning a foundation model in‑house.** Resonode consumes open/commercial models only.
- Outbound distribution/sending of communications (Resonode analyses and advises; it does not send). Integration with sending tools is read/advise only.
- Real‑time biometric capture of individuals (no webcam/eye‑tracking of the client's own staff); predictions are model‑based.

---

## 6. Personas and primary users

| Persona | Role in product | Primary needs |
|---|---|---|
| **Comms Manager** | Core analyst/creator | Score artifacts, see weaknesses, get recommendations, compare versions |
| **Internal Comms Lead** | Internal channels | Channel‑fit guidance, pre‑send checks, sentiment/safe‑framing |
| **Exec‑Office Writer** | CEO/leadership comms | Tone, key‑message clarity, exec‑presence (AV), high‑stakes review |
| **L&D / Training Lead** | Training materials | Comprehension/cognitive‑load, clarity, structure |
| **Policy / Compliance Officer** | Policies, regulated comms | Plain‑language, inclusive language, risk/claim guardrails, audit |
| **Brand Manager** | Brand consistency | Brand‑voice alignment, terminology consistency, competitive benchmarking |
| **Admin / Owner** | Tenant administration | Standards library, roles, quality gates, dashboards |
| **ML / Platform Engineer (client/partner)** | Integration | API/SDK, model orchestration, connectors |
| **Security / IT** | Trust & compliance | SSO, residency, isolation, on‑prem, no‑train guarantee |

---

## 7. Key use cases / user journeys

1. **Pre‑send email/memo check (text fast lane):** Comms Manager pastes/uploads text → sub‑2s clarity/tone/brand score + inline fixes → edits → re‑checks → sends from their own tool.
2. **Town‑hall deck review:** Exec‑Office Writer uploads a PowerPoint → per‑slide attention heatmaps, key‑message clarity, brand fit, composite score, recommendations → compares two versions → exports a report for the CEO's office.
3. **Policy/training comprehension audit:** Policy Officer uploads a policy PDF → readability/plain‑language, cognitive‑load, jargon/acronym, inclusivity and risk‑language flags → fixes → re‑scores → routes through approval.
4. **Recorded exec video:** Internal Comms Lead uploads a town‑hall recording → transcript + second‑by‑second attention/emotion timeline + delivery cues → recommendations on weak moments.
5. **Back‑catalogue baseline:** Admin connects SharePoint and queues a bulk audit of existing comms → org‑level comms‑health dashboard and trends.

---

## 8. Architecture overview (reference)

Resonode is layered so the model is replaceable and the value sits in the surrounding layers.

```
┌──────────────────────────────────────────────────────────────────────┐
│  6. EXPERIENCE LAYER  — Web app · Office/Outlook/Teams add‑ins · API/SDK │
├──────────────────────────────────────────────────────────────────────┤
│  5. GOVERNANCE LAYER  — Brand/standards library · Workflow & approval ·  │
│                         Quality gates · Audit · Model governance        │
├──────────────────────────────────────────────────────────────────────┤
│  4. INSIGHT LAYER     — Scores · Heatmaps · Timelines · Recommendations ·│
│                         Benchmarks · Reports · Analytics                │
├──────────────────────────────────────────────────────────────────────┤
│  3. MAPPING & CALIBRATION LAYER  (CORE IP)                              │
│     Raw model outputs → comms metrics (attention, comprehension,        │
│     memorability, emotion, brand) · calibration · validation            │
├──────────────────────────────────────────────────────────────────────┤
│  2. MODEL ORCHESTRATION LAYER                                          │
│     Pluggable model abstraction · routing per metric/modality ·         │
│     TRIBE v2 (primary) + specialised open models · versioning           │
├──────────────────────────────────────────────────────────────────────┤
│  1. INGESTION & RENDERING LAYER                                         │
│     Upload/connect · parse docx/pdf/pptx · ASR for AV · render to       │
│     model‑expected modalities · engineering‑artifact exclusion          │
├──────────────────────────────────────────────────────────────────────┤
│  0. PLATFORM FOUNDATION  — Multi‑tenant · security · privacy · residency │
│                            · scalable inference · observability         │
└──────────────────────────────────────────────────────────────────────┘
```

**Architectural principles (mandatory):**
- **Model‑agnostic:** no business logic may hard‑depend on a specific model's output shape; all model access goes through the orchestration layer's common interface.
- **Stateless inference, stateful records:** every analysis run is reproducible (model + adapter + mapping + input hash recorded).
- **Tenant isolation by default:** no cross‑tenant data or model context bleed.
- **Privacy‑first:** PII handled per Section 15; no content used to train shared models.

---

## 9. Functional requirements

> Grouped into 18 functional modules (E01–E18) matching the delivery epics. Each FR: ID · statement · acceptance criteria · phase · traceability. "Type" = Foundation / Parity / Differentiator. Priority = MoSCoW.

### E01 — Audience, Brand & Objective Context
- **FR-E01-1 Audience & persona library** *(Foundation, Must, Phase 1, TCA‑001)* — Users can define and reuse named audience segments with attributes (role, region, language, seniority). **AC:** create/edit/delete named audiences; attributes include region/language/role; reusable across analyses; default org audiences seeded.
- **FR-E01-2 Brand voice & messaging codification** *(Differentiator, Must, Phase 1, TCA‑002)* — Users can capture tone‑of‑voice, terminology (do/don't) and approved messaging pillars digitally. **AC:** stored, versioned, and applied during scoring; editable by Brand Manager role.
- **FR-E01-3 Communication objective tagging** *(Parity, Should, Phase 1, TCA‑003)* — Each artifact can be tagged with an objective (inform/align/persuade/reassure/drive action). **AC:** objective selectable; metric weighting changes by objective; shown in the report.
- **FR-E01-4 Artifact taxonomy & engineering exclusion** *(Foundation, Must, Phase 1, TCA‑004)* — Configurable taxonomy of comms artifact types with engineering artifacts excluded. **AC:** artifact types configurable; code/engineering docs blocked or flagged out‑of‑scope; type drives applicable checks.
- **FR-E01-5 Standards & policy library** *(Foundation, Must, Phase 1, TCA‑005)* — Central versioned library of brand, tone, terminology and compliance rules. **AC:** per‑artifact‑type rule sets; publish/rollback; applied org‑wide.
- **FR-E01-6 Multi‑language audience support** *(Parity, Should, Phase 2, TCA‑006)* — Analyse comms in English plus priority languages. **AC:** language auto‑detect; per‑language norms; Indic scripts supported.

### E02 — Multimodal Artifact Ingestion
- **FR-E02-1 Document & slide upload** *(Parity, Must, Phase 1, TCA‑007)* — Upload Word, PDF, PowerPoint. **AC:** parse docx/pdf/pptx incl. text, layout, images; slide structure preserved; OCR for scanned PDFs.
- **FR-E02-2 Text‑only fast lane** *(Parity, Must, Phase 1, TCA‑008)* — Paste/upload plain text for instant scoring. **AC:** sub‑2s clarity/tone/brand scoring without full multimodal run; upgrade to full analysis on demand.
- **FR-E02-3 Audio & video ingestion** *(Differentiator, Should, Phase 2, TCA‑009)* — Upload recordings (town‑halls, exec videos). **AC:** accept mp4/mov/wav/mp3; ASR transcript with timestamps; transcript aligned to frames; second‑by‑second timeline.
- **FR-E02-4 Live URL / intranet & email‑HTML capture** *(Parity, Should, Phase 2, TCA‑010)* — Analyse a URL or email HTML in context. **AC:** render URL/HTML to image+DOM; above‑the‑fold capture; auth via connector; snapshot stored.
- **FR-E02-5 Presentation‑as‑experience rendering** *(Differentiator, Could, Phase 3, TCA‑011)* — Render a deck as a timed viewing sequence. **AC:** per‑slide + flow score; pacing/overload flags.
- **FR-E02-6 Engineering‑artifact exclusion filter** *(Foundation, Should, Phase 2, TCA‑012)* — Auto‑detect and exclude engineering artifacts. **AC:** classifier flags code/eng docs; excluded with reason; admin‑only override.

### E03 — Model Orchestration & Inference Layer (TRIBE v2 + open models)
- **FR-E03-1 TRIBE v2 (open model) integration** *(Foundation, Must, Phase 1, TCA‑013)* — Integrate TRIBE v2 inference. **AC:** artifact rendered to the model's expected modalities; inference via managed/hosted serving; raw outputs captured per artifact/segment; **no in‑house training**.
- **FR-E03-2 Pluggable model‑abstraction & routing layer** *(Differentiator, Must, Phase 1, TCA‑014)* — Model‑agnostic interface; TRIBE v2 primary, others addable. **AC:** common inference interface; route per metric/modality; add/swap models via config; changing the model requires no app rewrite.
- **FR-E03-3 Output‑to‑comms‑metric mapping & calibration (core IP)** *(Differentiator, Must, Phase 1, TCA‑015)* — Map raw model signals to comms metrics. **AC:** mapping converts raw outputs to 0–100 comms metrics; calibrated and documented; validated against human ground‑truth.
- **FR-E03-4 Model selection & licence fit** *(Foundation, Must, Phase 1, TCA‑016)* — Each model's licence checked against commercial use. **AC:** per‑model licence review; TRIBE v2 used in production ONLY under a commercial licence from Meta, OR restricted to internal/eval with production inference routed to a commercially‑usable model; legal sign‑off recorded.
- **FR-E03-5 Multi‑model orchestration & specialised models** *(Differentiator, Should, Phase 2, TCA‑017)* — Combine specialised models per metric. **AC:** per‑metric model assignment; results merged with a consistent scoring contract; configurable per artifact type.
- **FR-E03-6 Segment‑level granularity** *(Differentiator, Should, Phase 2, TCA‑018)* — Score per slide/paragraph/scene. **AC:** per‑segment scoring; timeline for AV; drill‑down to weakest segments.
- **FR-E03-7 Model & adapter versioning, reproducibility** *(Foundation, Must, Phase 1, TCA‑019)* — Every score tied to model+adapter+input hash. **AC:** versions stamped on every result; re‑run reproduces score; changelog maintained.

### E04 — Attention & Visual Saliency
- **FR-E04-1 Predicted‑attention heatmaps** *(Parity, Must, Phase 1, TCA‑020)* — Heatmap over slide/email. **AC:** saliency overlay; focus order; AOI scoring; export PNG.
- **FR-E04-2 First‑seconds / above‑the‑fold analysis** *(Differentiator, Should, Phase 2, TCA‑021)* — What lands first. **AC:** early‑attention score; flag if key message/brand outside high‑salience zone; reposition recommendation.
- **FR-E04-3 Visual hierarchy & clutter check** *(Parity, Should, Phase 2, TCA‑022)* — Hierarchy/clutter on decks. **AC:** clutter/complexity score; competing‑focal‑point flags; per‑slide; benchmarked.

### E05 — Emotional Response & Tone
- **FR-E05-1 Emotional response prediction** *(Differentiator, Should, Phase 2, TCA‑023)* — Predict emotional response. **AC:** emotion spectrum per artifact/segment with intensity + valence; flag unintended negative emotion.
- **FR-E05-2 Tone‑of‑voice detection vs target** *(Parity, Should, Phase 1, TCA‑024)* — Detected tone vs target. **AC:** tone profile; gap vs target; sentence‑level tone flags.
- **FR-E05-3 Sensitive‑message safe‑framing check** *(Differentiator, Should, Phase 2, TCA‑025)* — Check change/restructuring comms for fear/ambiguity. **AC:** detect alarming/ambiguous framing; suggest reassuring alternatives; log review.
- **FR-E05-4 Executive‑presence / delivery read (AV)** *(Differentiator, Could, Phase 3, TCA‑026)* — Delivery cues in exec videos. **AC:** pace/filler/emphasis from transcript+audio; suggestions; **no biometric storage of the speaker without consent**.

### E06 — Comprehension, Clarity & Cognitive Load
- **FR-E06-1 Readability & plain‑language scoring** *(Parity, Must, Phase 1, TCA‑027)* — Readability/plain‑language on policies/training. **AC:** readability indices; long/passive/ambiguous‑sentence flags; jargon list; grade‑level vs target.
- **FR-E06-2 Cognitive‑load / comprehension prediction** *(Differentiator, Should, Phase 2, TCA‑028)* — Predicted cognitive load. **AC:** cognitive‑demand per section; overload flags; chunking suggestions; benchmarked.
- **FR-E06-3 Jargon, acronym & terminology check** *(Parity, Must, Phase 1, TCA‑029)* — Flag undefined acronyms/off‑list jargon. **AC:** detect undefined/inconsistent acronyms; flag banned jargon; suggest plain alternatives.
- **FR-E06-4 Key‑message clarity & findability** *(Differentiator, Should, Phase 2, TCA‑030)* — Is the core message clear and easy to find. **AC:** identify stated key message; score prominence/clarity; flag if buried; suggest stronger lead.
- **FR-E06-5 Structure & scannability check** *(Parity, Should, Phase 1, TCA‑031)* — Headings/length/bullets. **AC:** structure score; long‑block/missing‑heading flags; suggested chunking; per channel.

### E07 — Memorability & Message Retention
- **FR-E07-1 Memorability / recall prediction** *(Differentiator, Should, Phase 2, TCA‑032)* — Predicted memorability of key message. **AC:** predicted recall for key message + overall; weak‑retention flags; second‑by‑second for AV.
- **FR-E07-2 Message‑salience map** *(Differentiator, Could, Phase 3, TCA‑033)* — Which points are most/least memorable. **AC:** rank points by predicted retention; suggest repetition/placement; export.

### E08 — Brand Voice, Tone & Consistency Governance
- **FR-E08-1 Brand‑alignment scoring** *(Parity, Must, Phase 1, TCA‑034)* — Score vs codified brand voice. **AC:** brand‑alignment score; deviations with reasons + fixes; per‑section; trend over time.
- **FR-E08-2 Terminology & messaging consistency** *(Parity, Should, Phase 2, TCA‑035)* — Consistency across a set. **AC:** cross‑doc terminology/claims consistency; conflict flags; campaign‑level view.
- **FR-E08-3 In‑tool real‑time guidance** *(Differentiator, Should, Phase 2, TCA‑036)* — Live guidance while writing in Office. **AC:** sidebar flags brand/tone/clarity inline; one‑click fixes; score updates live.
- **FR-E08-4 Generative‑AI content governance** *(Differentiator, Should, Phase 2, TCA‑037)* — Score/guardrail AI‑generated drafts. **AC:** score LLM output vs standards; block off‑brand/non‑compliant; offer fixes; logged.

### E09 — Effectiveness Scoring & Benchmarking
- **FR-E09-1 Composite communication‑effectiveness score** *(Differentiator, Must, Phase 1, TCA‑038)* — One headline score. **AC:** weighted composite 0–100 with sub‑scores; objective‑weighted; pass/needs‑work threshold.
- **FR-E09-2 Internal benchmarks & norms** *(Parity, Should, Phase 2, TCA‑039)* — Benchmark vs org best + type norms. **AC:** percentile vs org history + artifact‑type norm; top‑quartile threshold; growing norms DB.
- **FR-E09-3 Variant A/B comparison** *(Parity, Should, Phase 2, TCA‑040)* — Compare two versions. **AC:** side‑by‑side scores + deltas; highlight changes; recommend winner with reason.
- **FR-E09-4 Competitive comms benchmarking** *(Differentiator, Could, Phase 3, TCA‑041)* — Benchmark public comms vs peers. **AC:** score public peer comms; relative positioning; respects copyright/ToS.

### E10 — Generative Recommendations & Rewrite
- **FR-E10-1 Actionable recommendations** *(Differentiator, Should, Phase 2, TCA‑042)* — Specific fixes for weak segments. **AC:** prioritised fixes per weakness; expected uplift; rationale; dismiss/accept.
- **FR-E10-2 Recommendation explainability & evidence** *(Parity, Should, Phase 2, TCA‑043)* — Cite the driver. **AC:** each recommendation links to metric + segment evidence; expected uplift; accept/track.
- **FR-E10-3 AI rewrite assist (guardrailed)** *(Differentiator, Could, Phase 3, TCA‑044)* — On‑brand AI rewrites. **AC:** rewrites honour brand voice + compliance; before/after predicted score; human approval required.
- **FR-E10-4 Predicted‑uplift simulation** *(Differentiator, Could, Phase 3, TCA‑045)* — Preview score if changes accepted. **AC:** re‑score edited draft instantly; show uplift vs baseline; log decision.

### E11 — Channel & Format Optimization
- **FR-E11-1 Channel‑specific guidance** *(Parity, Should, Phase 2, TCA‑046)* — Guidance tuned to channel. **AC:** channel profiles with format rules; channel‑aware scoring + tips; subject‑line/preview checks for email.
- **FR-E11-2 Subject‑line & hook optimization** *(Parity, Could, Phase 3, TCA‑047)* — Score/improve subject lines and hooks. **AC:** generate/score variants; predicted open/read; pick + insert.

### E12 — Authoring Integrations
- **FR-E12-1 Microsoft Word & PowerPoint add‑ins** *(Parity, Must, Phase 1, TCA‑048)* — Analyse from within Office. **AC:** add‑ins analyse current doc/deck; inline results; SSO; supports the M365 tenant.
- **FR-E12-2 Outlook & Teams pre‑send integration** *(Parity, Should, Phase 2, TCA‑049)* — Pre‑send analysis. **AC:** check in Outlook/Teams; warn/block on low score (configurable); one‑click report.
- **FR-E12-3 API & SDK for embedding** *(Parity, Should, Phase 2, TCA‑050)* — Embed analysis. **AC:** REST API + SDK; auth/keys; rate limits; webhook results; documentation.

### E13 — Workflow, Review & Approval Gates
- **FR-E13-1 Review & approval workflow** *(Parity, Should, Phase 2, TCA‑051)* — Draft→review→approve with sign‑off. **AC:** stages; reviewers; comments; sign‑off; status tracked; audit trail.
- **FR-E13-2 Quality gates / score thresholds** *(Differentiator, Should, Phase 2, TCA‑052)* — Minimum scores before publish. **AC:** configurable thresholds; block/warn; override with reason logged; per artifact type.
- **FR-E13-3 Collaboration & comments** *(Parity, Could, Phase 3, TCA‑053)* — Comment/assign fixes. **AC:** threaded comments; assign; resolve; @mentions; notifications.
- **FR-E13-4 Report export & sharing** *(Parity, Should, Phase 2, TCA‑054)* — Shareable report. **AC:** branded PDF/HTML with scores, heatmaps, recs; shareable link with access control.

### E14 — Analytics, Dashboards & Program Insights
- **FR-E14-1 Comms‑health dashboard** *(Foundation, Should, Phase 2, TCA‑055)* — Org‑level effectiveness over time. **AC:** trends by score, channel, team, artifact type; cohort views; export.
- **FR-E14-2 Team & author scorecards** *(Parity, Could, Phase 3, TCA‑056)* — Per‑team/author trends. **AC:** scorecards; improvement trend; privacy‑aware aggregation.
- **FR-E14-3 Pre‑send predicted‑engagement estimate** *(Differentiator, Could, Phase 3, TCA‑057)* — Predicted open/read before send. **AC:** predicted range vs norms; drivers; improve‑then‑recheck loop.
- **FR-E14-4 ROI & outcome correlation** *(Differentiator, Could, Phase 3, TCA‑058)* — Correlate predicted scores with actual engagement. **AC:** join predicted scores to downstream engagement; correlation report; caveats shown.

### E15 — Compliance, Inclusivity & Risk Guardrails
- **FR-E15-1 Inclusive & non‑discriminatory language** *(Parity, Must, Phase 1, TCA‑059)* — Inclusive‑language checks. **AC:** flag non‑inclusive terms; suggest alternatives; configurable per region/culture.
- **FR-E15-2 Regulated‑claim & risk‑language guardrails** *(Differentiator, Should, Phase 2, TCA‑060)* — Flag risky/over‑promising language. **AC:** detect unsupported claims/risk phrases; tie to policy library; review queue.
- **FR-E15-3 Data‑privacy consent & DPDP/GDPR** *(Foundation, Must, Phase 1, TCA‑061)* — Lawful processing of personal data in artifacts. **AC:** consent/processing basis; PII detection + redaction option; data‑subject rights; retention controls.

### E16 — Model Governance, Explainability & Validation
- **FR-E16-1 Explainable scores** *(Differentiator, Should, Phase 2, TCA‑062)* — Show why a score is what it is. **AC:** drivers per score; segment attributions; plain‑language explanation; no black box.
- **FR-E16-2 Accuracy validation & norms** *(Foundation, Must, Phase 1, TCA‑063)* — Validate vs human ground‑truth. **AC:** held‑out human tests; reported accuracy per metric; drift monitoring; published methodology.
- **FR-E16-3 Bias & fairness checks** *(Differentiator, Should, Phase 2, TCA‑064)* — Check for bias across languages/regions. **AC:** bias tests across segments; disparity reporting; mitigation log; model card.
- **FR-E16-4 Model cards & human‑in‑the‑loop** *(Foundation, Should, Phase 2, TCA‑065)* — Documentation + human review controls. **AC:** model card (scope, data, limits); human review required for high‑stakes; override logging.
- **FR-E16-5 Audit log of analyses & overrides** *(Foundation, Should, Phase 2, TCA‑066)* — Append‑only governance log. **AC:** append‑only audit (actor/time/artifact/action/override reason); exportable.

### E17 — Security, Privacy, IP & Data Residency
- **FR-E17-1 Enterprise SSO & RBAC** *(Foundation, Must, Phase 1, TCA‑067)* — SSO + role‑based access. **AC:** SAML/OIDC SSO; SCIM; granular roles; access audit.
- **FR-E17-2 Data residency & tenant isolation** *(Foundation, Must, Phase 1, TCA‑068)* — India/EU residency + isolation. **AC:** region‑pinned storage; per‑tenant isolation; encryption in transit/at rest; key management.
- **FR-E17-3 On‑prem / private / air‑gapped deployment** *(Differentiator, Should, Phase 2, TCA‑069)* — Private/on‑prem option. **AC:** VPC/on‑prem/air‑gapped options; no data egress; customer‑managed keys; documented.
- **FR-E17-4 Content IP & no‑training guarantee** *(Differentiator, Must, Phase 1, TCA‑070)* — Contractual no‑train‑on‑our‑content. **AC:** zero‑retention/no‑train option; per‑tenant model boundaries; auditable; in contract.
- **FR-E17-5 PII detection & redaction in artifacts** *(Foundation, Should, Phase 2, TCA‑071)* — Detect/redact PII. **AC:** detect PII; redact/mask option; configurable; logged; no PII in logs.

### E18 — Platform Foundation, API & Reliability
- **FR-E18-1 Scalable inference architecture** *(Foundation, Must, Phase 1, TCA‑072)* — Autoscaling inference. **AC:** autoscaling; queue + batch; SLA latency targets; cost controls.
- **FR-E18-2 Async batch audit jobs** *(Parity, Should, Phase 2, TCA‑073)* — Queue large back‑catalogue audits. **AC:** bulk job queue; progress/status; partial results; completion notification.
- **FR-E18-3 Multi‑tenant SaaS foundation** *(Foundation, Should, Phase 2, TCA‑074)* — Multi‑tenant isolation + per‑tenant config. **AC:** tenant isolation; per‑tenant brand/audience config; usage metering; admin separation.
- **FR-E18-4 Observability & reliability** *(Foundation, Should, Phase 1, TCA‑075)* — Monitoring/alerting/audit. **AC:** metrics/logs/traces; uptime SLO; alerting; append‑only audit of actions.
- **FR-E18-5 Connector & integration framework** *(Foundation, Could, Phase 3, TCA‑076)* — Pluggable connectors. **AC:** M365/Google/DAM/CMS connectors; auth; per‑connector permissions; certified M365/Google.

---

## 10. Non‑functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR‑01 | Performance | Text‑only analysis p95 < 2s; full artifact (≤50pp deck/policy) p95 < 60s; AV processing ≤ 2× real‑time. |
| NFR‑02 | Scalability | Support ≥ [N] concurrent analyses and batch audits of ≥ 10,000 artifacts `[NEEDS CLARIFICATION: peak concurrency target]`. |
| NFR‑03 | Availability | ≥ 99.5% monthly (Phase 2), ≥ 99.9% (Phase 3); documented RTO ≤ 4h, RPO ≤ 1h. |
| NFR‑04 | Security | TLS 1.2+ in transit, AES‑256 at rest; secrets in a vault; key rotation; align to ISO 27001; SOC 2 Type II target. |
| NFR‑05 | Privacy & compliance | DPDP 2023 (India) and GDPR; PII detection/redaction; configurable retention; data‑subject rights; no content used to train shared models. |
| NFR‑06 | Data residency | Region‑pinned storage (India and/or EU per tenant); cross‑border transfer controls. |
| NFR‑07 | Deployment | SaaS multi‑tenant default; private VPC; on‑prem/air‑gapped option for regulated clients. |
| NFR‑08 | Accessibility | WCAG 2.2 AA for all end‑user surfaces. |
| NFR‑09 | Localisation | English + Hindi at minimum; priority languages configurable; correct Indic‑script rendering in UI and exports. |
| NFR‑10 | Reliability/observability | Centralised logging/metrics/tracing; alerting; append‑only audit logs; no PII in logs. |
| NFR‑11 | Maintainability | Model‑agnostic abstraction; CI/CD with automated tests; golden‑set regression for mapping/calibration. |
| NFR‑12 | Reproducibility | Every analysis reproducible from model+adapter+mapping+input hash. |
| NFR‑13 | Cost control | Inference cost per analysis tracked and capped; caching of repeated/identical analyses. |
| NFR‑14 | Licensing | No model used in production in violation of its licence (see Section 13); licence register maintained. |

---

## 11. Data model (key entities)

- **Tenant/Organization** — id, name, region, deployment type, retention policy.
- **User** — id, tenant, role(s), SSO identity.
- **Role** — Owner, Admin, Comms Manager, Internal Comms Lead, Exec‑Office Writer, L&D Lead, Policy/Compliance Officer, Brand Manager, Reviewer, ML/Platform Eng, Security; permission sets.
- **Audience/Persona** — id, attributes (role/region/language/seniority).
- **BrandProfile / StandardsLibraryItem** — voice attributes, terminology, messaging pillars, rules; versioned.
- **Artifact** — id, type, channel, owner, status; **ArtifactVersion** — content ref, render output, hash.
- **AnalysisRun** — id, artifact version, objective, audience, model+adapter+mapping versions, timestamp, status.
- **MetricScore** — run id, metric (attention/emotion/comprehension/memory/brand/clarity/inclusivity/risk), value 0–100, confidence, drivers.
- **Segment** — run id, locus (slide/paragraph/scene/timestamp), per‑metric scores.
- **Recommendation** — run id, segment, issue, suggested fix, expected uplift, status (accepted/dismissed).
- **ModelRegistryEntry** — model name, version, licence, modality, metric coverage, status.
- **Benchmark/Norm** — artifact type, metric, distribution, percentile thresholds.
- **Workflow/Approval** — artifact, stage, reviewer, decision, sign‑off.
- **AuditLog** — actor, time, entity, action, reason (append‑only).
- **Connector** — tenant, type, auth, permissions.
- **Report** — run(s) ref, format, access control, share link.

---

## 12. Integrations & external interfaces

- **Microsoft 365:** Word, PowerPoint, Outlook, Teams add‑ins; SharePoint connector.
- **Google Workspace:** Docs/Slides/Drive connector (Phase 3).
- **Identity:** SAML/OIDC (Entra ID, Okta, Ping); SCIM provisioning.
- **Models:** TRIBE v2 (primary, via managed serving) and additional open/commercial models behind the orchestration abstraction.
- **DAM/CMS:** pluggable connectors (Phase 3).
- **Outbound:** REST API + SDK; webhooks for async results.
- **Reporting:** PDF/HTML export; shareable links with access control.

---

## 13. Model & licensing requirements

1. **No in‑house foundation‑model training.** Resonode consumes open/commercial models only.
2. **Model‑agnostic abstraction (FR‑E03‑2)** is mandatory and is the enabler for the licensing strategy.
3. **TRIBE v2 licence (CC BY‑NC 4.0):** production inference on TRIBE v2 is permitted **only** under (a) a commercial licence obtained from Meta, **or** (b) a configuration where TRIBE v2 is used for internal R&D/evaluation only and production inference is routed to a commercially‑usable model. **The build must support both without code change** (config‑switchable model routing).
4. **Licence register (NFR‑14):** maintain a register of every model, its version and licence terms; CI gate blocks deploying a model whose licence does not permit the intended use.
5. **Mapping & calibration (FR‑E03‑3)** is owned IP and must be model‑independent so swapping models preserves the comms‑metric contract.
6. Always re‑verify current model licence terms with the model owner before each release.

---

## 14. AI/ML governance & explainability

- Every metric score must expose its **drivers** and a plain‑language explanation (FR‑E16‑1).
- **Validation** against human ground‑truth per metric, with published methodology and accuracy, plus drift monitoring (FR‑E16‑2).
- **Bias/fairness** testing across languages/regions with disparity reporting (FR‑E16‑3).
- **Model cards** and **human‑in‑the‑loop** for high‑stakes outputs (FR‑E16‑4).
- Outputs are positioned as **decision support, not guaranteed outcomes** — UI copy must reflect this.

---

## 15. Security, privacy & compliance requirements

- SSO + RBAC (FR‑E17‑1); tenant isolation + residency (FR‑E17‑2); on‑prem/air‑gapped option (FR‑E17‑3).
- **No‑training‑on‑customer‑content guarantee**, contractually and technically enforced (FR‑E17‑4).
- PII detection and optional redaction before analysis; no PII in logs (FR‑E17‑5).
- DPDP 2023 + GDPR: consent/processing basis, data‑subject rights, retention controls (FR‑E15‑3).
- Append‑only audit logging of analyses, overrides and AI rewrites (FR‑E16‑5).

---

## 16. Analytics & reporting

- Org‑level comms‑health dashboard with trends and cohorts (FR‑E14‑1).
- Team/author scorecards (privacy‑aware) (FR‑E14‑2).
- Pre‑send predicted‑engagement estimate (FR‑E14‑3) and outcome correlation (FR‑E14‑4).
- Exportable, access‑controlled analysis reports (FR‑E13‑4).

---

## 17. UX / UI requirements — key screens

1. **Home/Dashboard** — recent analyses, comms‑health summary, quick‑analyze entry.
2. **Analyze** — upload/paste/connect; objective + audience selectors; progress.
3. **Analysis Report** — composite score + sub‑scores; per‑segment view; attention heatmaps; AV timeline; recommendations with accept/track; export.
4. **A/B Compare** — side‑by‑side with deltas and recommended winner.
5. **Standards & Brand Admin** — voice, terminology, rules, versions.
6. **Audience Manager** — segments and attributes.
7. **Workflow/Approval** — stages, reviewers, sign‑off, quality‑gate status.
8. **Analytics** — trends, scorecards, cohorts.
9. **Model & Governance Admin** — model registry, licences, validation/accuracy, model cards, audit.
10. **Settings/Security** — SSO, roles, residency, retention, connectors, no‑train toggle.

UI must meet WCAG 2.2 AA and render Indic scripts correctly. Provide an embeddable lightweight result view for the Office/Outlook sidebar.

---

## 18. Release plan / phasing

**Phase 1 — Pilot / MVP (≈28 requirements):** a credible analyser for one pilot client. Text + document/slide ingestion and rendering; TRIBE v2 integration + model abstraction + mapping/calibration + licence fit + versioning; attention heatmaps; tone vs target; readability/plain‑language/jargon/structure; brand‑alignment; composite score; Word/PowerPoint add‑ins; inclusive language; DPDP/GDPR + consent; SSO + RBAC + residency + no‑train; validation/accuracy; scalable inference + observability. **Exit:** pilot client running weekly analyses with validated accuracy and signed‑off licensing.

**Phase 2 — Scale (≈36 requirements):** multimodal (audio/video) + URL/intranet; multi‑model orchestration + segment granularity; emotional response + safe‑framing; cognitive‑load + key‑message clarity; memorability; consistency + in‑tool guidance + AI‑content governance; benchmarks + A/B; recommendations + explainability; channel guidance; Outlook/Teams + API/SDK; workflow + quality gates + report export; dashboards; risk‑language guardrails; explainability + bias + model cards + audit; on‑prem option + PII redaction; batch audits + multi‑tenant. **Exit:** multi‑tenant SaaS with governance, sold to a second client.

**Phase 3 — Advanced (≈12 requirements):** deck‑as‑experience; exec‑presence AV; message‑salience; competitive benchmarking; AI rewrite + uplift simulation; subject‑line/hook optimization; collaboration; scorecards + predicted‑engagement + ROI correlation; connector framework. **Exit:** differentiated platform with predictive and generative depth.

---

## 19. Definition of Done (global)

A requirement/story is Done when: code merged via CI with passing automated tests; acceptance criteria demonstrably met; mapping/calibration regression (golden set) green where relevant; security/privacy checks passed (no PII in logs, residency honoured); accessibility check (WCAG 2.2 AA) for UI; telemetry/audit emitted; documentation and (where applicable) API docs updated; model/version stamping verified for any analysis‑producing change.

---

## 20. Assumptions, constraints & dependencies

- **Assumptions:** pilot client provides representative artifacts and brand standards; a managed serving option exists for TRIBE v2 (or chosen model); accuracy thresholds agreed with client.
- **Constraints:** TRIBE v2 non‑commercial licence (Section 13); confidential exec/board comms drive residency/no‑train/on‑prem; engineering artifacts excluded.
- **Dependencies:** model serving infrastructure; identity provider; M365 tenant access for add‑ins; legal sign‑off on model licensing.

---

## 21. Open questions / `[NEEDS CLARIFICATION]`

1. Client‑accepted **accuracy/validity threshold** per metric (gates GA) — Section 3.2 / FR‑E16‑2.
2. **Peak concurrency** and expected monthly analysis volume — NFR‑02.
3. **TRIBE v2 production path:** commercial licence from Meta vs. routing production inference to a commercially‑usable model — FR‑E03‑4 / Section 13.
4. **Priority languages** beyond English/Hindi for Phase 2 — FR‑E01‑6 / NFR‑09.
5. **Pilot client identity and artifact corpus** for validation norms — Section 9 E09/E16.
6. **On‑prem/air‑gapped** required at GA or Phase 3 for the first target accounts — FR‑E17‑3.
7. **Hosting region(s)** and whether EU residency is needed alongside India — NFR‑06.
8. Whether **outbound sending‑tool integrations** (Poppulo/Staffbase/PoliteMail) are required for engagement‑correlation — FR‑E14‑4.

---

## 22. Glossary

- **Analyser** — application that consumes models to score communications; does not train models.
- **Artifact** — a communication deliverable submitted for analysis.
- **Mapping/Calibration layer** — converts raw model outputs to comms metrics; the product's core IP.
- **TRIBE v2** — Meta FAIR tri‑modal model predicting human brain response; CC BY‑NC 4.0.
- **Composite effectiveness score** — weighted blend of metric sub‑scores.
- **Quality gate** — minimum score threshold before publish.

---

## 23. Appendix — traceability

All 76 functional requirements map 1:1 to backlog stories `TCA-001`–`TCA-076` in *Enterprise Comms NeuroAnalyzer Competitive Backlog.xlsx* (Backlog and Epic Summary sheets), which also carry the competitive benchmark source for each capability. Phasing, Type (Foundation/Parity/Differentiator) and Market Coverage are inherited from that backlog.

*End of document.*
