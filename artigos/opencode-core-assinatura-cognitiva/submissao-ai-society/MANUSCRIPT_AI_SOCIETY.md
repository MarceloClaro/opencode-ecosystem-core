# The house that helps to think: authored cognitive prostheses, agentic AI, and the care of memory

**Subtitle:** A self-study of a self-built agentic ecosystem

**Article type:** Open Forum

**Word count:** approximately 7,500 words in the main text (excluding abstract, references, tables, and supplementary material)

---

## Abstract

Most software is designed for a generic user. This article examines the inverse case: an AI system built by the person who uses it, in response to a specific cognitive vulnerability. The system analyzed here — referred to as the Core — is a monorepo for agentic orchestration, scientific research, and evidence production. Its creator reports giftedness (high ability) and an elevated risk of Alzheimer's disease. Drawing on a documentary case study of the repository, this article describes the cycle Perceive–Specify–Delegate–Execute–Verify–Reflect and shows how it externalizes memory, executive function, attention, and verification. It proposes the concept of the *authored cognitive prosthesis* and argues that the system's cognitive signature is a situated configuration of documentable choices, not a biomarker or a mental portrait. Five marks of that signature are identified: memory treated as fragile, the contract before the impulse, verification against conviction, an architecture of interruption, and a didactic vocation. The article then discusses the risks — overload, dependency, automation bias, and the bureaucratization of care — and proposes a pre-registered N-of-1 evaluation protocol with clinical oversight. It concludes that the Core may help its creator sustain continuity, memory, and agency, but it does not prevent, treat, or diagnose Alzheimer's disease. Its value depends on preserving social ties, contestability, and the human capacity to stop.

**Keywords:** cognitive prosthesis; agentic AI; cognitive signature; extended mind; care; Alzheimer's risk

---

## 1. Introduction

Most software is written for a generic user. This article examines the inverse case: a system built by the person who uses it, in response to a vulnerability that person knows from the inside. The system analyzed here — referred to as the Core — is a monorepo for agentic orchestration, scientific research, and the production of evidence. It connects agents, MCP servers, formal specifications, tests, evolution records, a book, a scientific pipeline, and a metacognitive memory layer. Its golden rule is unusual: no delivery without a specification, a test, and evidence. The central question of the project is not “how many agents exist?” but “what was executed, with which source, which hash, and which limit?” (Core Project, 2026b).

This article starts from an interpretive hypothesis: that design is not only technical. It carries the mark of a way of thinking and of a condition of life. The creator reports giftedness (high ability) and an elevated risk of Alzheimer's disease. Giftedness is often associated with systemic thinking, hyperfocus, rapid pattern recognition, and high intellectual standards; it can also come with executive overload, perfectionism, and difficulty stopping. The risk of Alzheimer's disease makes the finitude of memory salient and gives urgency to the act of leaving traces. The architecture responds to this double context with externalized memory, contracts, verification, and resumption.

The thesis is this: the Core is an **authored cognitive prosthesis**. “Prosthesis” is not used in the medical sense of replacing tissue, but in the sense of an external structure that carries part of the cognitive load and gives the user back time, order, and the possibility of continuing. “Authored” because it was conceived by the person who uses it and because it materializes documentable choices made by its creator. The cognitive signature, here, is not a biomarker, a personality test, or a proof of artificial consciousness. It is a **situated configuration of choices** — questions considered important, ways of decomposing problems, acceptance criteria, rules of memory, and declared limits (Core Project, 2026a).

The article makes four contributions. First, it proposes an operational definition of the authored cognitive prosthesis, distinct from totalizing metaphors such as the “second brain.” Second, it describes the architecture of the Core and shows how each mechanism responds to a cognitive function. Third, it examines the risks of this form of assistance — dependency, overload, automation bias, and the bureaucratization of care. Fourth, it proposes an N-of-1 evaluation protocol, pre-registered and with clinical oversight, so that the hypothesis of benefit can be tested rather than presumed. Throughout, it foregrounds the societal dimension: who has access to cognitive prostheses, who is accountable for their outputs, and what happens to care when memory is delegated to a machine.

The method is documentary and interpretive. There was no clinical, neuropsychological, or experimental assessment of the author. The analysis relies on the code, specifications, tests, evolution records, and documentation of the repository, as well as literature on extended cognition, cognitive load, giftedness, and cognitive reserve. The article distinguishes **observation** (what the repository contains), **interpretation** (what those choices suggest), and **prescription** (what should be evaluated). That distinction separates a critical analysis from a piece of self-promotion.

A note on care is necessary. Giftedness is not a disease. The phrase “suffering from giftedness,” common in everyday speech, captures the distress that can accompany the mismatch between capacity and environment, but it does not name a nosological category. Risk of Alzheimer's disease is not a diagnosis. This article does not claim that the Core prevents, treats, or diagnoses any condition; it does not claim that giftedness causes Alzheimer's disease; and it does not offer medical advice. The system described here has not been validated as a neuroprotective intervention. The hypothesis that it may help is a research question, not a result.

The article proceeds as follows. Section 2 develops the conceptual framework. Section 3 presents the case and the method. Section 4 discusses giftedness and Alzheimer's risk as design conditions. Section 5 describes the architecture. Section 6 proposes the reading of the cognitive signature. Section 7 distinguishes what the prosthesis does from what it does not do. Section 8 examines risks and safeguards. Section 9 presents the evaluation protocol. Section 10 discusses the house, the architect, and time. Section 11 concludes.

## 2. Conceptual framework

### 2.1 From the extended mind to scaffolded cognition

Clark and Chalmers (1998) proposed that cognitive processes can extend beyond the skull. The classic example is Otto's notebook, which functions as a reliable and accessible external memory. The “parity principle” suggests that if an external process performs the same function as an internal one, it deserves the same cognitive status. The thesis is philosophical, not clinical: it shifts the unit of analysis from the brain to the person–environment system.

The thesis has critics. Rupert (2004) argues that extended cognition does not adequately explain the integration and persistence of internal processes. Sterelny (2010) proposes a more modest alternative: the mind is **scaffolded** by external structures, but not every scaffold becomes part of the cognitive system. This distinction is useful here. The Core is not presented as a literal part of the author's mind. It is a **robust scaffold**, a structure that carries part of the load and changes how the task is performed.

The lineage matters. Bush's (1945) memex and Engelbart's (1962) program for augmenting human intellect already imagined external systems that would help people think. The Core belongs to that lineage, but it adds a distinctive feature: it is not only a tool for storing or retrieving information; it is a system for **governing** the conditions under which a claim can be made, a task can be resumed, and a memory can be trusted.

### 2.2 Cognitive artifacts and offloading

Norman (1991) showed that cognitive artifacts do not merely store information: they transform the task. A checklist is not a passive reminder; it reorganizes the sequence, reduces dependence on working memory, and makes error more visible. The same applies to a specification, an automated test, or a receipt with a hash. These artifacts do not “think” for the user; they change the economy of attention.

Cognitive load theory (Sweller, 1988) explains why the mind has limits: working memory processes few novel elements at once, and overload impairs learning. Cognitive offloading — using the environment to reduce internal demand — is an adaptive response (Risko & Gilbert, 2016). But offloading has costs. If a user outsources remembering, they may remember less; if they outsource calculation, they may calculate less; if they outsource verification, they may trust more than they should. The question is not whether offloading is good or bad in the abstract, but whether it preserves the functions the user wants to keep exercised and whether it transfers to the system decisions that require human judgment.

### 2.3 Distributed cognition and responsibility

Hutchins (1995) showed that the cognition of a cockpit is not only in the pilots' heads: it is distributed across people, instruments, procedures, and representations. Hollan, Hutchins, and Kirsh (2000) extended this approach to human–computer interaction. The unit of analysis is the coordinated system, not the isolated individual.

The Core is a distributed cognitive system: the author, the agents, the MCP servers, the specifications, the tests, and the records form a network that produces decisions. But there is an ethical asymmetry: only the author is accountable for what the system does. The distribution of cognition does not distribute responsibility. This asymmetry is the foundation of Section 7.

### 2.4 Cognitive reserve and the limits of prevention

Cognitive reserve is one of the most cited and most misunderstood hypotheses in the field. It suggests that the relation between pathology and symptom is not fixed: people with more cognitive resources may tolerate more pathology before manifesting symptoms (Stern, 2002). The practical implication is often simplified as “use it or lose it.” The literature is more cautious. Intellectual activity, social life, physical exercise, control of vascular factors, and education are associated with lower risk of dementia in observational studies (Livingston et al., 2020), but effect sizes vary, populations are heterogeneous, and causality is difficult to establish.

For this article, cognitive reserve matters for two reasons. First, it offers a language for thinking about the value of a cognitively rich environment without turning that language into a promise. Second, it imposes a limit: if the Core helps the author maintain engagement, routine, and social ties, it may contribute to what the literature calls reserve; but this must be tested, not presumed. Alzheimer's disease is, in contemporary research, defined by a biological continuum, with markers that can precede symptoms by decades (Jack et al., 2018). Dementia is a clinical syndrome with functional impact. Risk is a probabilistic estimate that combines genetics, vascular and metabolic factors, education, physical activity, hearing, social life, depression, and other factors (Livingston et al., 2020). Risk is not destiny; diagnosis is not prognosis; prognosis is not sentence.

No software has been validated as a neuroprotective intervention. A system like the Core can, at most, reduce environmental demands, support routines, externalize memory, and preserve continuity. These effects are plausible, but they need to be measured. This article treats them as research hypotheses, not results.

### 2.5 Definition: the authored cognitive prosthesis

On the basis of these traditions, the article defines the **authored cognitive prosthesis** as:

> a technical-artifactual system, conceived by its own user, that externalizes mnemonic, executive, and epistemic functions and materializes a style of decision; its evaluation depends on its capacity to preserve the user's agency, not on its capacity to replace the user.

The definition has three consequences. First, it is functional, not medical: a cognitive prosthesis does not need to be implanted or prescribed to be useful. Second, it is authored: the system carries choices made by the person who built it, and those choices can be examined. Third, it is normative: the criterion of success is not “doing more faster,” but “preserving the possibility that the user remains the author of their decisions.”

### 2.6 The cognitive signature

The project's design preface defines the **authored cognitive signature** as “this situated configuration of documentable choices” (Core Project, 2026a). The definition is deliberately modest. It does not claim that code reveals the author's mind; it claims that code preserves marks of the author's questions, criteria, representations, and decisions. The strong version — that every ecosystem would reveal, in a unique and recoverable way, the cognition of a single creator — exceeds the available evidence.

This modesty is necessary for three reasons. First, authorship is composite: the Core uses libraries, models, data, inherited practices, and contributions from agents. Second, the relation between code and cognition is not transparent: the same style can be produced by different motivations. Third, interpretation can become mythology: the author can confuse their own narrative with a proof. Stylistic attribution from technical artifacts has limits; it can preserve regularities, but it does not measure personality or cognition (Caliskan et al., 2018).

## 3. Case and method

### 3.1 The case

The Core is a public monorepo maintained by the author. The local checkout analyzed on 10 November 2026 (Git base `1ce6ae98`) records 35 MCP servers, 35 commands, and 374 agent entries in `opencode.json`. The reconciled block in `README.md` records 366 agents and 35 MCPs; the divergence between counts is a reminder that an inventory is not a single portrait and that documentation also has a history. The repository contains 681 specification files in the `SPEC-*.md` pattern, 646 test files, and 845 evolution cycles. These are counts of files or configuration. None of them measures quality, availability, authentication, inference, or external validation.

The Core organizes operation around a six-move cycle: Perceive → Specify → Delegate → Execute → Verify → Reflect. The cycle is not a rigid sequence; it is a grammar of governance (Core Project, 2026b, 2026c). Each move has mechanisms, artifacts, and limits. The architecture includes a CLI, an orchestrator, a specification and test layer, a metacognitive memory layer, a trust and incentive layer, a catalog of agents, and a presentation and documentation layer.

### 3.2 Method

The article adopts the instrumental case study (Yin, 2018): the Core matters less for itself than for the phenomenon it illuminates — the construction of a cognitive prosthesis by its own user. The corpus includes:

- architecture and operation documents (`README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `MANUAL.md`, `CORRIGENDUM.md`);
- the R909 preface on cognitive signature and its specification;
- modules for memory, orchestration, verification, trust, economy, and evolution;
- evolution records and counts of specifications and tests;
- external literature on cognition, learning, giftedness, and dementia.

The analysis is documentary, not experimental. There was no execution of the system to measure performance, no cognitive testing of the author, and no access to medical records, biomarkers, or neuropsychological assessment. Claims about the code are verifiable in the cited files. Claims about the author's cognition are interpretations based on his self-report and his textual production, not diagnoses. The manuscript was prepared with AI assistance for preliminary drafting, structural editing, and reference formatting. The author reviewed, rewrote, and verified the text and takes full responsibility for the content. A detailed statement is provided in the Statements and Declarations.

### 3.3 Position and bias

The creator is also the main user of the system. This produces an advantage — access to the design process — and a risk: confirmation bias, the tendency to seek and interpret information in ways that support prior beliefs (Nickerson, 1998). The Core itself incorporates a response to this risk: the `CORRIGENDUM.md`, a public document of self-correction of claims; the metacognitive gate, which does not return “verified” without explicit external validation; and the requirement of specification, test, and receipt. These mechanisms do not eliminate bias. They make it visible and contestable — which is the most an architecture can promise.

### 3.4 Limits

The limits are explicit. First, this is a single case; it cannot be generalized to other people with giftedness, other creators, or other forms of neurocognitive risk. Second, there are no clinical data: the risk of Alzheimer's disease is reported, not diagnosed. Third, the counts age: specifications, tests, and cycles change with every commit. Fourth, the scores of the cycles are self-assessment, not an external benchmark (Core Project, 2026e). Fifth, no cognitive, functional, or clinical outcome was measured. Sixth, a metaphor is not a mechanism: calling modules “memory,” “attention,” or “metacognition” does not make them measures of the human mind (Poldrack, 2011). The boundary between description and diagnosis requires caution; the RDoC, for example, is a research framework, not a clinical instrument (Insel et al., 2010).

## 4. The user-creator: high ability, asynchrony, and risk

### 4.1 Giftedness is not a disease

Giftedness (high ability) designates a profile of high potential, with heterogeneous manifestations in specific domains, combined with creativity and task commitment (Renzulli, 1978). Developmental models add that talent is built over time, in conditions of learning, support, and recognition (Gagné, 2004). In Brazil, educational law recognizes giftedness as a category served by special education (Brasil, 1996, 2008), which does not solve the problem of identification but confirms that it is an educational and developmental issue, not a pathology.

The phrase “suffering from giftedness,” used in the report that originated this article, does not correspond to a nosological category. It captures something real: the distress that can accompany the asynchrony between capacity and environment — the distance between what a person can think and what the context allows them to do. That distress is not giftedness itself; it is the mismatch. This article preserves the report and adopts the more precise formulation: the author **reports giftedness**.

The literature on giftedness warns against two reductionisms. The first is the single-IQ reduction: reducing giftedness to a measure of intelligence leaves out creativity, motivation, specific domains, and trajectory. The second is the label reduction: treating identification as destiny rather than as a starting point for support. Heterogeneity is the rule. Two people with giftedness can have very different cognitive, emotional, and social profiles.

### 4.2 Strengths and costs

In the author's report, the profile is associated with systemic thinking, rapid pattern recognition, hyperfocus, and high standards. These are resources: they allow crossing domains, building complex architectures, and sustaining long projects. They also have costs. Hyperfocus can erase the perception of time and basic needs. High standards can turn every delivery into a debt. Associative speed can produce a sense of evidence that the data do not yet support. Sensitivity to inconsistency can make it difficult to live with imperfect systems — including one's own body.

These costs are neither universal nor diagnostic. They are working hypotheses, useful because they explain why certain architectural choices appear in the Core: budgets, timeouts, checkpoints, specifications, tests, receipts. The system was designed **as if** attention could fail, memory could be lost, and conviction could deceive. This is a form of operational humility.

### 4.3 Risk of Alzheimer's disease: risk is not diagnosis

The author reports an elevated risk of Alzheimer's disease. It is important to distinguish three planes. **Alzheimer's disease** is, in contemporary research, defined by a biological continuum, with markers that can precede symptoms by decades (Jack et al., 2018). **Dementia** is a clinical syndrome with functional impact. **Risk** is a probabilistic estimate that combines genetics, vascular and metabolic factors, education, physical activity, hearing, social life, depression, and other factors (Livingston et al., 2020). Risk is not destiny; diagnosis is not prognosis; prognosis is not sentence.

The notion of **cognitive reserve** helps to think about the problem without promising miracles. The hypothesis is that life experiences — education, intellectual work, social engagement, complex activities — may allow a person to cope better with pathology before symptoms become disabling (Stern, 2002). This does not mean that a specific activity prevents the disease. The literature is observational, heterogeneous, and subject to reverse causation: those with more reserve may be precisely those who had more opportunities, health, and resources throughout life.

No software has been validated as a neuroprotective intervention. A system like the Core can, at most, reduce environmental demands, support routines, externalize memory, and preserve continuity. These effects are plausible, but they need to be measured. The article treats them as research hypotheses, not results.

### 4.4 Double vulnerability as a design constraint

What matters here is not speculation about a causal relation between giftedness and Alzheimer's disease — there is no basis for that — but the **design constraint** that arises when someone with high cognitive demand and fear of loss builds a system not to lose themselves. Table 1 summarizes this translation.

**Table 1. From reported vulnerability to architectural hypothesis**

| Reported vulnerability | Design hypothesis | Mechanism in the Core | Limit |
|---|---|---|---|
| Loss of context between sessions | Externalized, retrievable memory | MetaBus, `shared_memory.json`, confidence ledger | Selective memory; not a total backup |
| Difficulty starting and sequencing long tasks | Contracts and decomposition | Specs, acceptance criteria, DAGs, leases | Requires human intention |
| Risk of confusing conviction with evidence | Independent verification | TDD, SpecVerifier, anti-overclaim gate | A test is not scientific truth |
| Hyperfocus and difficulty stopping | Budgets and limits | Timeouts, stop rules, doctor, helpdesk | The system does not control the user |
| Fear of losing continuity | Durable state and resumption | TaskRuntime, checkpoints, EvolutionRegistry | Preserves traces, not the person |
| Need for meaning and legacy | Documentation and teaching | Book, manual, MIRA, didactic pipeline | Does not measure pedagogical efficacy |

The table does not say that the system “solves” these vulnerabilities. It says that it was designed **as if** they existed. That distinction is decisive: an architecture can be epistemically useful without being therapeutically effective.

## 5. The architecture of the Core

### 5.1 Overview

The Core organizes operation around six moves:

```text
Perceive → Specify → Delegate → Execute → Verify → Reflect
```

The cycle is a grammar of governance, not a rigid sequence. Table 2 summarizes the translation between cognitive function and architecture.

**Table 2. Cognitive functions and architectural mechanisms**

| Move | Externalized function | Mechanism | Evidence | Limit |
|---|---|---|---|---|
| Perceive | Context and memory | MetaBus, shared memory, confidence ledger | `mci/metabus.py` | Selective memory; last 1,000 events |
| Specify | Intention and criteria | SpecRegistry, SpecVerifier, acceptance criteria | `sdd/spec_engine.py`, `specs/` | A spec does not guarantee execution |
| Delegate | Division of labor and attention | Blackboard A2A, Agent Cards, Trust Engine | `mci/blackboard.py`, `trust/` | Agents are not people |
| Execute | Sequencing and persistence | TaskRuntime, DAG, leases, budget | `mci/task_runtime.py` | Does not decide what matters |
| Verify | Reality testing | TDD, SpecVerifier, BehavioralGate, anti-overclaim | `sdd/tdd_runner.py`, `mci/metacognitive_gate.py` | A test is not scientific truth |
| Reflect | Consolidation and learning | Reflexion, EvolutionRegistry, lessons | `mci/reflexion.py`, `evolution/cycles.py` | Self-assessment is not external validation |

### 5.2 Perceive: memory as a workspace

The MetaBus is described as a “unified metacognitive event bus” and a “shared memory” among agents. It maintains episodic memory, semantic memory, and a **confidence ledger** — a record of confidence by agent or topic. The declared inspiration is Global Workspace Theory, the Reflexion framework, and collaborative memory in multi-agent systems (Core Project, 2026f).

In practice, the MetaBus does three things. First, it publishes events: task requests, conclusions, reflections, failures. Second, it allows agents to subscribe to events. Third, it persists a state that can be consulted before a new decision. Memory is selective: the code keeps the last 1,000 episodic events. This is a design choice, not a detail. A system that tried to remember everything would have cost, noise, and risk of contamination. Selectivity is a form of productive forgetting.

The externalized cognitive function is **context**. The author does not need to reconstruct from memory what has already been decided, tested, or discarded. But the MetaBus is not a backup of the mind. It records traces, not lived experience. The difference matters: a trace can be consulted; an experience must be interpreted.

### 5.3 Specify: the contract before the impulse

The SpecRegistry carries formal specifications; the SpecVerifier verifies acceptance criteria; the TDDRunner produces test evidence. The rule is explicit: no delivery without a specification, a test, and evidence. The practice of writing the test before the implementation is the basis of TDD (Beck, 2002). In the analyzed checkout, there are 681 specification files in the `SPEC-*.md` pattern. A specification is not a bureaucratic document: it is the place where intention becomes criterion.

The externalized cognitive function is **executive function**: keeping the goal stable, decomposing it into steps, defining what counts as done. For someone with hyperfocus, the specification works as a rail. For someone at risk of overload, it works as a limiter: it is not necessary to decide everything again in each session. For someone inclined to confuse conviction and evidence, it works as a contract against their own volatility.

The limit is clear: a specification can become an end in itself. The Core has 681 specifications; this is both a wealth and a risk. The wealth is in traceability; the risk is in bureaucratization. A system that requires a specification for every gesture can paralyze the gesture.

### 5.4 Delegate: the Blackboard and the economy of trust

The Blackboard implements a shared board on which agents volunteer for tasks based on **Agent Cards** — descriptions of capabilities, input schema, and status. The blackboard pattern is classic in AI systems (Nii, 1986), and the notion of an agent as an autonomous system that perceives and acts in an environment comes from the agent literature (Wooldridge & Jennings, 1995). Selection weighs declared capabilities, historical confidence, and load. The Trust Engine maintains scores by action, applies a behavioral gate, and records outcomes. The Token Economy adds stake, slashing, and a fee market (Core Project, 2026f).

The externalized cognitive function is the **division of labor**. The author does not need to execute everything; he publishes a task, receives volunteers, and chooses. The metaphor is that of a market, but the mechanism is one of governance: trust is historical, load is a limit, and stake is a commitment. An agent with a bad history loses priority; an overloaded agent is passed over; an agent that fails can be slashed.

There are two risks. The first is **false objectivism**: a confidence score is not a measure of truth. An agent can have high trust and produce a wrong answer with confidence. The second is **false merit**: stake measures commitment, not competence. The token economy is a coordination device, not an epistemology.

### 5.5 Execute: the architecture of interruption

The TaskRuntime implements nanogranular task graphs, with states, leases, budgets, and recovery. The inspiration is a local and deterministic runtime that does not depend on the network or on global services. The important detail for this article is that the runtime **assumes interruption**. It was designed so that a task can be resumed, not so that the user never stops.

The externalized cognitive function is **sequencing and persistence**. The system maintains state, grants leases, expires attempts, and records results. The author can leave, return, and continue. For a person at risk of fatigue or loss of context, this is more than convenience: it is a way of preserving the continuity of work without demanding that the body and attention be constant.

The limit is that the runtime does not decide what matters. It can execute very well a task that should not be done. Prioritization remains human. The architecture of interruption does not replace the architecture of desire.

### 5.6 Verify: reality testing

Verification is the epistemic heart of the Core. The TDDRunner produces test evidence; the SpecVerifier checks criteria; the BehavioralGate authorizes or blocks actions based on trust; the metacognitive gate classifies the degree of a claim and **does not return “verified” without explicit external validation**. The `CORRIGENDUM.md` records claims that sounded stronger than the available evidence and proposes the correct reading.

The externalized cognitive function is **reality testing**. The system does not prevent the author from believing something; it makes it harder to declare that something has been proven when it has not. For someone with a high capacity to build coherent narratives, this is a necessary counterweight. The internal coherence of an explanation is not proof of its truth; a test that passes is not proof that the test measures what it should measure; a high score is not proof of merit.

The limit is the same as that of any verification system: it only verifies what has been specified. A test can confirm a wrong hypothesis, a specification can formalize an inadequate criterion, a gate can block a correct action. Verification is a practice, not a certainty machine. The literature on reproducibility shows that apparent results may not hold (Ioannidis, 2005).

### 5.7 Reflect: consolidation and record

The ReflexionEngine, inspired by Shinn et al. (2023), generates post-task reflections and publishes them to the MetaBus; the EvolutionRegistry records cycles with objective, changes, score, lessons, hashes, and state anchors. The analyzed `cycles.json` has 845 entries. The externalized cognitive function is **consolidation**: turning an execution into a lesson, and a lesson into a memory that can be retrieved.

Reflection has two effects. The first is technical: the system learns from failures and adjusts routes. The second is existential: the author leaves a trace of his path. In a context of risk of memory loss, that trace has value in itself. It does not preserve the person, but it preserves decisions, justifications, and lessons. It is a form of indirect continuity.

The limit is that self-assessment is not external validation. The scores of the cycles are assigned by the process itself; the `CORRIGENDUM.md` acknowledges that the average of 9.4/10 is not a benchmark. Reflection can become self-justification if there is no counterproof. The Core has counterproof mechanisms — tests, adversarial review, external gate — but they do not eliminate the risk.

### 5.8 The human layer: orientation and teaching

Beyond the orchestration core, the Core includes a layer of orientation and teaching: the `doctor` (diagnosis), the `helpdesk` (guided help), the manual (Core Project, 2026d), the book, the MIRA presentation pipeline, and the Book Studio. This layer dialogues with principles of multimedia design (Mayer & Moreno, 2003), without proving pedagogical efficacy; the approximation to neuroscience requires caution against neuromyths (Howard-Jones, 2014). The layer is not accessory. It externalizes **orientation** — the capacity to know where one is and what to do next — and the **didactic vocation** — the will to turn one's own path into material for others.

For the author, this layer has a double value. It helps him orient himself when context disperses, and it turns the knowledge built into a legacy. For the reader, it is a door. For the critic, it is a risk: excessive documentation can create the illusion that the system is more understood than it is.

## 6. The cognitive signature

### 6.1 What it is and what it is not

The project's design preface defines the **authored cognitive signature** as “this situated configuration of documentable choices” (Core Project, 2026a). The definition is deliberately modest. It does not claim that code reveals the author's mind; it claims that code preserves marks of his questions, criteria, representations, and decisions. The strong version — that every ecosystem would reveal, in a unique and recoverable way, the cognition of a single creator — exceeds the available evidence. Stylistic attribution from technical artifacts has limits; it can preserve regularities, but it does not measure personality or cognition (Caliskan et al., 2018).

This modesty is necessary for three reasons. First, authorship is composite: the Core uses libraries, models, data, inherited practices, and contributions from agents. Second, the relation between code and cognition is not transparent: the same style can be produced by different motivations. Third, interpretation can become mythology: the author can confuse his own narrative with a proof.

### 6.2 Five marks

Even so, five marks are documentable. They do not exhaust the signature; they are an interpretive cut.

**1. Memory treated as fragile.** The system is built as if memory could fail. There is shared memory, a confidence ledger, specifications, receipts, hashes, state anchors. This choice is not only technical: it is an existential stance. The author does not trust remembrance; he trusts the record. The sentence “what was executed, with which source, which hash, and which limit?” is a response to the possibility of forgetting.

**2. The contract before the impulse.** The rule “no delivery without a specification” subordinates inspiration to a form. For a creator with high fluency and hyperfocus, this is counterintuitive: the will to make comes before the contract. The architecture inverts the order. The contract does not deny the impulse; it protects it from itself, preventing enthusiasm from redefining the criterion of success halfway through.

**3. Verification against one's own conviction.** The anti-overclaim gate, the `CORRIGENDUM.md`, and the requirement of external validation are a response to the tendency to confuse coherence with truth. This is perhaps the most distinctive mark of the Core. It is not about distrusting others; it is about distrusting one's own capacity to build a convincing narrative. The architecture turns that distrust into procedure.

**4. The architecture of interruption.** The runtime assumes that the task can be interrupted; the MetaBus assumes that context can be lost; the `doctor` assumes that the environment can be broken. The system is made to resume, not to demand continuous presence. This mark is especially significant in a context of neurocognitive risk: the architecture does not promise perfect memory, but it promises a way back.

**5. The didactic vocation.** The book, the manual, MIRA, the explainers, and the concern with the “democratization of knowledge” show that the signature is not only in the code. It is in the will to teach what was learned. This mark has an ethical dimension: knowledge is not treated as property, but as something that should be made accessible — with limits, sources, and warnings.

**Table 3. Five marks of the cognitive signature**

| Mark | Evidence in the Core | Interpretation | Counterevidence |
|---|---|---|---|
| Memory treated as fragile | MetaBus, hashes, receipts, state anchors | Distrust of remembrance; trust in the record | The system keeps only the last 1,000 events |
| Contract before impulse | Specs, acceptance criteria, TDD | Protection of intention against volatility | A spec can become bureaucracy |
| Verification against conviction | Anti-overclaim gate, `CORRIGENDUM.md` | Distrust of coherent narratives | Self-assessment remains self-assessment |
| Architecture of interruption | DAGs, leases, checkpoints, resumption | Design for fatigue and loss of context | The user can still overwork |
| Didactic vocation | Book, manual, MIRA, explainers | Knowledge as a common good | Documentation is not pedagogical efficacy |

### 6.3 Composite authorship

The “mirroring” hypothesis suggests that the modularity of a system can reflect the coordination style of those who produce it (MacCormack et al., 2012). Distributed cognition suggests that the relevant unit is the person–instrument–procedure system, not the isolated individual (Hutchins, 1995). Both traditions converge on a composite reading: the signature of the Core is not a portrait of the author, but the result of an interaction among author, tools, models, community, and history.

This does not dissolve authorship. The author chose the questions, the criteria, the priorities, and the limits. He also chose to use agents and models, and he chose to record that choice. The signature is less in the details of the code than in the **way of responding to uncertainty**: documenting, testing, correcting, asking for review. It is a signature of responsibility. Technological mediation materializes values and choices, but it does not guarantee that they are virtuous (Verbeek, 2006).

### 6.4 The risk of myth

Every interpretation of authorship runs the risk of becoming myth. The myth has three forms. The first is **celebration**: turning the architecture into proof of genius. The second is **justification**: using the signature to explain or excuse failures. The third is **prison**: believing that the author can only create in one way, and that the signature is a destiny.

The article refuses all three. The signature is an interpretive hypothesis, not an essence. Generalization from a single case requires caution (Yarkoni, 2022). It can be contested by counterexamples: choices that contradict the pattern, contributions that come from others, moments when the system fails. The very existence of the `CORRIGENDUM.md` is a counterproof to the temptation to celebrate. A system that corrects itself publicly is not a monument; it is a work in progress.

## 7. What the prosthesis does and does not do

### 7.1 What it does

The Core can help the author in several concrete ways:

- **It reduces switching cost.** Context is recorded; the author does not need to reconstruct it at every session.
- **It externalizes executive function.** Specs, criteria, and DAGs turn intention into sequence.
- **It expands verification capacity.** Tests, gates, and receipts make error more visible.
- **It preserves continuity.** Durable state allows resumption after an interruption.
- **It distributes work.** Agents and MCP servers take on repetitive or specialized tasks.
- **It documents the path.** The record of cycles and lessons creates an indirect memory.
- **It supports teaching.** The book, the manual, and MIRA turn the path into material for others.
- **It creates a space for contestation.** The `CORRIGENDUM.md` and the anti-overclaim gate open the system to criticism.

These benefits are plausible, but they have not been measured. Section 9 proposes how to measure them.

### 7.2 What it does not do

The Core **does not** prevent Alzheimer's disease. It **does not** treat dementia. It **does not** diagnose. It **does not** replace sleep, exercise, nutrition, social life, medical or psychological care. It **does not** guarantee correct decisions. It **does not** eliminate biases. It **does not** preserve the person; it preserves traces. It **does not** make the author immortal.

This list may seem obvious, but it is necessary. The language of the “second brain,” “augmented memory,” and “personal agent” can easily slide into the promise that the system compensates for what biology does not. The architecture of the Core, with its emphasis on evidence and limits, offers resources to resist that temptation. But the temptation does not disappear because the system has a `CORRIGENDUM.md`.

### 7.3 The paradoxes of the prosthesis

Every cognitive prosthesis carries paradoxes.

**The paradox of offloading.** The more the system carries memory, the less the user exercises memory. This can be good (freeing resources for high-level tasks) or bad (losing practice). The answer is not to abandon offloading; it is to create deliberate moments of practice without a net.

**The paradox of recording.** The more the system records, the more the user must navigate records. Excess documentation can become a second overload. The answer is to prune, hierarchize, and create criteria of relevance.

**The paradox of verification.** The more the system verifies, the more the user may trust the system and the less they verify on their own. The answer is to keep human verification at critical points and to train judgment, not only tool use.

**The paradox of personalization.** The more the system adapts to the user, the harder it is for others to use it and the harder it is for the user to leave. The answer is to document, export, and maintain open standards.

### 7.4 The ethical question

If the tool was made for one user, what happens to others? The Core is both idiosyncratic and universal. It was born from a singular need, but its patterns — externalized memory, contracts, verification, resumption — are generalizable. The ethical question is to prevent the prosthesis from becoming a privilege: access to hardware, energy, time, and technical knowledge is not equally distributed.

The project's response is partial: an MIT license, a local-first emphasis, and open documentation. This does not solve inequality, but it creates conditions for others to adapt. The authored prosthesis is justified only if it can be contested, reproduced, and modified by others. Otherwise, it is merely a private extension of privilege.

## 8. Risks and safeguards

Table S3 in the supplementary material summarizes the main risks and the existing or proposed safeguards. No safeguard eliminates risk; they make it manageable.

### 8.1 The second disease

There is a risk that deserves its own name: the prosthesis can become a **second disease**. A system that demands specs, tests, reviews, updates, and maintenance can consume the life it was supposed to protect. The author can spend more time caring for the architecture than living what the architecture should make possible. Hyperfocus, which is a strength, can ally itself with perfectionism and turn the Core into a labyrinth.

This risk is not hypothetical. The repository has 681 specs, 646 tests, and 845 cycles. The wealth is real; the cost is also real. The architecture needs **stop rules** — explicit criteria for stopping, publishing, resting, and leaving something imperfect. Without them, the prosthesis turns against the user.

### 8.2 Humane defaults

The Core is, in many places, **fail-closed**: when in doubt, it blocks. This is appropriate for safety, but it can be inhuman. A system that blocks too much can paralyze; one that demands too much can exclude. The proposal of “humane defaults” is that the system, when it fails, offers a way out: an explanation, an alternative, a human contact, a way to continue.

This is especially important for a user with neurocognitive risk. If the system does not understand the context, it should say “I don't know” and offer help, not insist on a route. If the user is tired, the system should suggest a pause, not one more spec. The architecture of verification needs to be accompanied by an architecture of care.

## 9. Evaluation: an N-of-1 protocol

### 9.1 Why N-of-1

The case is unique, personalized, and heterogeneous. A traditional randomized trial is neither feasible nor ethical for such a personal intervention. The N-of-1 design — or single-case experiment — allows hypotheses to be tested in one person, with repeated measures, alternated conditions, and pre-registration (Nosek et al., 2018). It does not produce statistical generalization, but it produces local evidence, useful for informed decisions.

The protocol below is a proposal. It was not executed. It should be adapted with health professionals, neuropsychologists, and research ethics review.

### 9.2 Outcomes

The primary outcomes should include time to resume after an interruption, task completion rate, error rate in routine tasks, perceived cognitive load (an adapted NASA-TLX), and calibration of trust (declared confidence versus accuracy). Secondary outcomes should include sense of agency, sleep and social life, and stress symptoms. The full outcome matrix is provided in the supplementary material. The selection should be finalized with a clinician.

### 9.3 Design

A possible design is an **ABAB with randomized blocks** over 12 weeks:

- **Phase A (without the Core):** the author performs comparable tasks with his usual tools, without the system.
- **Phase B (with the Core):** the author uses the system with the same tasks.
- **Repetition:** A and B alternate, with a one-week washout.
- **Randomization:** the order of blocks is randomized and recorded.
- **Blinding:** the evaluation of some outcomes (for example, the quality of an artifact) can be done by a third party who does not know in which phase the artifact was produced.
- **Pre-registration:** hypotheses, outcomes, analyses, and stopping criteria are registered before the start.

### 9.4 Analysis

The analysis can combine visual inspection of time series with mixed models to measure level change and trend. Effect sizes should be reported with uncertainty. Multiplicity of outcomes should be controlled or explicitly discussed. Negative results should be published. The analysis should not be performed by the same agent that implemented the intervention without independent supervision.

### 9.5 Ethics

The protocol requires informed consent and the possibility of withdrawal; protection of sensitive data; clinical supervision to interpret signs of cognitive decline; separation between research data and care data; review by an ethics committee when applicable; and a commitment not to turn the result into a claim of cure or prevention.

## 10. Discussion: the house, the architect, and time

The house metaphor, proposed in the project's design preface, organizes the conclusion. A house preserves decisions of those who conceived it, but it is not the person. It can be renovated, inhabited by others, abandoned. The Core is a house with several rooms: memory (MetaBus), the workshop (TaskRuntime), the library (specs, docs, book), the court (verification, `CORRIGENDUM`), the archive (EvolutionRegistry), and the classroom (manual, MIRA, explainers). Each room has a function; none of them is the architect's mind.

The temporal dimension is central. The risk of Alzheimer's disease makes the finitude of memory salient. The system is a wager against forgetting, but it cannot defeat mortality. It can preserve traces, not presence. It can allow the author to resume a project after a pause, but it cannot guarantee that he remembers why he started. The house helps to think, but it does not think for him.

The collective dimension is also central. The Core is a composite work: author, agents, libraries, models, community. The signature is the author's, but it is not only his. This composition is both a wealth and a responsibility. The wealth is in the possibility of doing more than one person would do alone; the responsibility is in not erasing the contributions of others or attributing to the author what is collective.

The political dimension is inescapable. Cognitive prostheses are not neutral. They require infrastructure, energy, time, and knowledge. If they are treated as a luxury, they will increase inequality; if they are treated as a right, they will require policies of access, training, and care. The Core, with its open license and local-first emphasis, is a contribution, not a solution. The question of who can build and maintain such a system is a question of distributive justice.

The epistemological dimension is the most delicate. The Core is a machine of humility: it demands spec, test, receipt, and correction. But humility can become a new form of pride — “my system is more rigorous than the others.” The `CORRIGENDUM.md` is the vaccine against this. It reminds us that rigor is a practice, not an identity. A system that corrects itself is not infallible; it is only more honest about its failures.

## 11. Conclusion

This article analyzed the Core as an authored cognitive prosthesis. The thesis was defended in three steps. First, the system externalizes concrete cognitive functions: memory, executive function, attention, verification, and reflection. Second, this externalization carries a signature: productive distrust of one's own memory, the primacy of the contract, verification against one's own conviction, the architecture of interruption, and the didactic vocation. Third, this signature is a situated interpretation, not a biomarker; it must be contested, not celebrated.

The context of giftedness and risk of Alzheimer's disease gives urgency to the project. Giftedness helps to explain the intensity, the complexity, and the demand for rigor; neurocognitive risk helps to explain the emphasis on memory, continuity, and resumption. But the article refused easy causality: there is no evidence that giftedness causes Alzheimer's disease, nor that the Core prevents the disease. What exists is a coherence of design: a system built to sustain the cognitive life of someone who knows his own fragility.

The main contribution is not the system itself, but the possibility of thinking about it critically. An authored cognitive prosthesis should be evaluated by what it preserves, not by what it promises. If the Core helps the author continue thinking, working, and teaching, it fulfills a function; if it prevents him from sleeping, from socializing, or from stopping, it fails. The criterion is not the number of agents, specs, or cycles. It is the quality of life that the architecture makes possible.

The research program that opens is clear: to measure, with an N-of-1 design and clinical supervision, the effects of the Core on resumption, cognitive load, errors, agency, and well-being; to compare it with simpler alternatives; to investigate the risks of dependency and deskilling; and to develop an ethics of cognitive prostheses that is both rigorous and humane.

The house does not replace the architect. It gives him back time and space to continue designing — and, when necessary, to leave.

---

## Statements and Declarations

**Competing interests.** The author declares no competing financial or non-financial interests. The author is the creator and main user of the system analyzed in this article. This relationship is disclosed here and is treated as a potential source of bias in Section 3.3.

**Funding.** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**Ethics approval and consent to participate.** This is a self-study based on documentary analysis of the author's own software project and on the author's self-report. It does not involve human participants other than the author, and no clinical, biometric, or identifiable third-party data were used. Ethical approval was therefore not required. The author consents to the publication of the self-report and of the analysis.

**Consent for publication.** The author is the sole participant and consents to publication.

**Data and code availability.** The code, specifications, tests, and evolution records are available in a public repository. The repository URL is withheld from the anonymized manuscript for double-blind review and is provided on the title page. The article does not report experimental data; the documentary corpus is described in Section 3.2.

**Preprint.** An earlier, Portuguese-language version of this article is available in the project's public repository. It has not been peer-reviewed. The present manuscript is a substantially revised and translated version.

**Use of AI.** The author used an AI assistant (an orchestrator based on DeepSeek V4.1 Flash, via OpenCode) for preliminary drafting, structural editing, and reference formatting. The author reviewed, rewrote, and revised the text, verified the sources, and takes full responsibility for the content. The AI is not an author and did not make interpretive or ethical decisions. A detailed account of the human–AI division of labor is provided in the title page.

**Author contributions.** The author conceived the study, designed the system, collected the documentary evidence, wrote and revised the manuscript, and approved the final version.

**Acknowledgements.** The author thanks the open-source communities whose libraries, models, and tools made the Core possible. The author also thanks the reviewers, whose criticism will improve the argument.

---

## References

Beck, K. (2002). *Test-driven development: By example*. Addison-Wesley.

Brasil. (1996). *Lei nº 9.394, de 20 de dezembro de 1996: Diretrizes e bases da educação nacional*. Presidência da República.

Brasil. (2008). *Política nacional de educação especial na perspectiva da educação inclusiva*. Ministério da Educação.

Bush, V. (1945). As we may think. *The Atlantic Monthly, 176*(1), 101–108.

Caliskan, A., Yamaguchi, F., Dauber, E., Harang, R., Rieck, K., Greenstadt, R., & Narayanan, A. (2018). When coding style survives compilation: De-anonymizing programmers from executable binaries. In *Proceedings of the Network and Distributed System Security Symposium (NDSS)*. https://doi.org/10.14722/ndss.2018.23304

Clark, A., & Chalmers, D. (1998). The extended mind. *Analysis, 58*(1), 7–19. https://doi.org/10.1093/analys/58.1.7

Core Project. (2026a). *Preface: The cognitive signature of an agentic ecosystem* [Design document]. In *the Core project*.

Core Project. (2026b). *The Core project* [Computer software]. GitHub. (URL withheld for double-blind review.)

Core Project. (2026c). *AGENTS.md* [Project documentation]. In *the Core project*.

Core Project. (2026d). *MANUAL.md* [Project documentation]. In *the Core project*.

Core Project. (2026e). *CORRIGENDUM.md* [Project documentation]. In *the Core project*.

Core Project. (2026f). *Modules*: `mci/metabus.py`, `mci/blackboard.py`, `mci/task_runtime.py`, `mci/reflexion.py`, `mci/metacognitive_evaluator.py`, `mci/metacognitive_gate.py`, `sdd/spec_engine.py`, `sdd/tdd_runner.py`, `trust/trust_engine.py`, `economy/token_economy.py`, `evolution/cycles.py`, `orchestrator.py`, `doctor.py` [Source code]. In *the Core project*.

Engelbart, D. C. (1962). *Augmenting human intellect: A conceptual framework* (Summary Report AFOSR-3223). Stanford Research Institute.

Gagné, F. (2004). Transforming gifts into talents: The DMGT as a developmental theory. *High Ability Studies, 15*(2), 119–147. https://doi.org/10.1080/1359813042000314682

Hollan, J., Hutchins, E., & Kirsh, D. (2000). Distributed cognition: Toward a new foundation for human-computer interaction research. *ACM Transactions on Computer-Human Interaction, 7*(2), 174–196. https://doi.org/10.1145/353485.353487

Howard-Jones, P. A. (2014). Neuroscience and education: Myths and messages. *Nature Reviews Neuroscience, 15*, 817–824. https://doi.org/10.1038/nrn3817

Hutchins, E. (1995). *Cognition in the wild*. MIT Press.

Insel, T., Cuthbert, B., Garvey, M., Heinssen, R., Pine, D. S., Quinn, K., Sanislow, C., & Wang, P. (2010). Research domain criteria (RDoC): Toward a new classification framework for research on mental disorders. *American Journal of Psychiatry, 167*(7), 748–751. https://doi.org/10.1176/appi.ajp.2010.09091379

Ioannidis, J. P. A. (2005). Why most published research findings are false. *PLoS Medicine, 2*(8), e124. https://doi.org/10.1371/journal.pmed.0020124

Jack, C. R., Bennett, D. A., Blennow, K., Carrillo, M. C., Dunn, B., Haeberlein, S. B., Holtzman, D. M., Jagust, W., Jessen, F., Karlawish, J., Liu, E., Molinuevo, J. L., Montine, T., Phelps, C., Rankin, K. P., Rowe, C. C., Scheltens, P., Siemers, E., Snyder, H. M., & Sperling, R. (2018). NIA-AA research framework: Toward a biological definition of Alzheimer's disease. *Alzheimer's & Dementia, 14*(4), 535–562. https://doi.org/10.1016/j.jalz.2018.02.018

Livingston, G., Huntley, J., Sommerlad, A., Ames, D., Ballard, C., Banerjee, S., Brayne, C., Burns, A., Cohen-Mansfield, J., Cooper, C., Costafreda, S. G., Dias, A., Fox, N., Gitlin, L. N., Howard, R., Kales, H. C., Kivimäki, M., Larson, E. B., Ogunniyi, A., … Mukadam, N. (2020). Dementia prevention, intervention, and care: 2020 report of the Lancet Commission. *The Lancet, 396*(10248), 413–446. https://doi.org/10.1016/S0140-6736(20)30367-6

MacCormack, A., Baldwin, C., & Rusnak, J. (2012). Exploring the duality between product and organizational architectures: A test of the mirroring hypothesis. *Research Policy, 41*(8), 1309–1324. https://doi.org/10.1016/j.respol.2012.04.011

Mayer, R. E., & Moreno, R. (2003). Nine ways to reduce cognitive load in multimedia learning. *Educational Psychologist, 38*(1), 43–52. https://doi.org/10.1207/S15326985EP3801_6

Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology, 2*(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175

Nii, H. P. (1986). Blackboard systems: The blackboard model of problem solving and the evolution of blackboard architectures. *AI Magazine, 7*(2), 38–53.

Norman, D. A. (1991). Cognitive artifacts. In J. M. Carroll (Ed.), *Designing interaction: Psychology at the human-computer interface* (pp. 17–38). Cambridge University Press.

Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences, 115*(11), 2600–2606. https://doi.org/10.1073/pnas.1708274114

Poldrack, R. A. (2011). Inferring mental states from neuroimaging data: From reverse inference to large-scale decoding. *Neuron, 72*(5), 692–697. https://doi.org/10.1016/j.neuron.2011.11.001

Renzulli, J. S. (1978). What makes giftedness? Reexamining a definition. *Phi Delta Kappan, 60*(3), 180–184.

Risko, E. F., & Gilbert, S. J. (2016). Cognitive offloading. *Trends in Cognitive Sciences, 20*(9), 676–688. https://doi.org/10.1016/j.tics.2016.07.002

Rupert, R. D. (2004). Challenges to the hypothesis of extended cognition. *Journal of Philosophy, 101*(8), 389–428. https://doi.org/10.5840/jphil2004101826

Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. In *Advances in Neural Information Processing Systems (NeurIPS)*. arXiv:2303.11366

Sterelny, K. (2010). Minds: Extended or scaffolded? *Phenomenology and the Cognitive Sciences, 9*(4), 465–481. https://doi.org/10.1007/s11097-010-9174-y

Stern, Y. (2002). What is cognitive reserve? Theory and research application of the reserve concept. *Journal of the International Neuropsychological Society, 8*(3), 448–460. https://doi.org/10.1017/S1355617702813248

Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science, 12*(2), 257–285. https://doi.org/10.1207/s15516709cog1202_4

Verbeek, P.-P. (2006). Materializing morality: Design ethics and technological mediation. *Science, Technology, & Human Values, 31*(3), 361–380. https://doi.org/10.1177/0162243905285847

Wooldridge, M., & Jennings, N. R. (1995). Intelligent agents: Theory and practice. *The Knowledge Engineering Review, 10*(2), 115–152. https://doi.org/10.1017/S0269888900008122

Yarkoni, T. (2022). The generalizability crisis. *Behavioral and Brain Sciences, 45*, e1. https://doi.org/10.1017/S0140525X20001685

Yin, R. K. (2018). *Case study research and applications: Design and methods* (6th ed.). Sage.

---

## Supplementary material

**Supplementary Table S1.** Repository indicators (10 November 2026; Git base `1ce6ae98`). Counts of specification files, test files, evolution cycles, configured agents, MCP servers, commands, and structural checks, with the corresponding limits of interpretation.

**Supplementary Table S2.** Proposed N-of-1 outcome matrix: outcome, instrument, frequency, hypothesis, and risk of distortion.

**Supplementary Table S3.** Risks and safeguards: manifestation, safeguard in the Core, additional safeguard needed, and residual risk.

**Supplementary Note S1.** Glossary of architectural terms: MetaBus, Blackboard, Agent Card, Trust Engine, BehavioralGate, TaskRuntime, SpecRegistry, SpecVerifier, EvolutionRegistry, and Token Economy.

**Supplementary Note S2.** Anonymized inventory of the documentary corpus and file paths used in the analysis.
