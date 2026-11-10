# The house that helps to think: authored cognitive prostheses, agentic AI, and the limits of epistemic sovereignty

**Subtitle:** A philosophical case study of a self-built agentic system

**Article type:** Original Research

**Word count:** approximately 8,000 words in the main text (excluding abstract, references, tables, and supplementary material)

---

## Abstract

This article examines a philosophical puzzle raised by self-built AI systems: when a person designs an agentic system to compensate for their own cognitive vulnerabilities, who authors the resulting cognition, and what kind of artifact is it? The article develops a case study of a self-built agentic system, referred to as the Core: a monorepo for agentic orchestration, memory externalization, and verification, built by a researcher who reports giftedness and an elevated risk of Alzheimer's disease. It argues for a moderate account of the cognitive prosthesis: the system is not a literal part of the mind, but a robust scaffold that transforms the task, redistributes epistemic labor, and materializes a style of responsibility. It introduces the concept of the cognitive signature as a situated configuration of documentable choices, not a biomarker. It identifies three epistemic risks — false objectivity, automation bias, and deskilling — and three ethical risks — dependency, the bureaucratization of care, and epistemic inequality. It proposes an N-of-1 epistemology to test claims about the prosthesis without overclaiming. The article concludes that the value of an authored prosthesis lies not in replacing the person, but in preserving agency, contestability, and the capacity to stop.

**Keywords:** cognitive prosthesis; extended mind; agentic AI; epistemic dependence; authorship; cognitive signature

---

## 1. Introduction: the puzzle of self-authored cognition

Imagine a person who builds a house for their own mind. The house has rooms for memory, for work, for verification, and for teaching. The house is not a thought experiment: it is a software system, built by the person who uses it, to compensate for cognitive vulnerabilities that they know from the inside. The system records what was decided, what was tested, and what remains uncertain. It delegates tasks to agents, checks their outputs, and refuses to call a claim “verified” without external validation. It is, in a word, a prosthesis.

The puzzle is not whether such a system is useful. It is what kind of thing it is, and who is responsible for what it does. Is the system an extension of the mind, in the sense defended by Clark and Chalmers (1998)? Is it a mere tool, causally useful but cognitively external? Is it a scaffold that transforms the task without becoming part of the cognitive system, as Sterelny (2010) suggests? Or is it a new kind of epistemic agent, whose outputs are co-authored by the human who designed it and the artificial agents that execute it? These questions are not idle. They bear on how we evaluate the system, how we assign responsibility for its errors, and how we care for the person who depends on it.

This article defends three claims. First, the Core is best understood as an **authored cognitive prosthesis**: a robust scaffold that carries part of the cognitive load and transforms the task, but does not constitute the mind. Second, its **cognitive signature** is a situated configuration of documentable choices — a style of responsibility, not a fingerprint. Third, the ideal of **epistemic sovereignty** that motivates such a system is necessarily limited: the prosthesis manages dependence on agents, models, and records, but it cannot eliminate it. By epistemic sovereignty, I mean the ideal of self-governance over one's own cognitive life: the capacity to decide what to believe, what to remember, and what to count as evidence, without being unduly dependent on others. The ideal is attractive, but it is necessarily limited by epistemic dependence. The ethical task is to make that dependence visible, contestable, and met with care.

The case is the **Core**, a monorepo for agentic orchestration, scientific research, and the production of evidence. The system connects agents, MCP servers, formal specifications, tests, evolution records, a book, a scientific pipeline, and a metacognitive memory layer. Its golden rule is unusual: no delivery without a specification, a test, and evidence. The central question of the project is not “how many agents exist?” but “what was executed, with which source, which hash, and which limit?” (Core Project, 2026b). The creator reports giftedness (high ability) and an elevated risk of Alzheimer's disease. Giftedness is often associated with systemic thinking, hyperfocus, rapid pattern recognition, and high intellectual standards; it can also come with executive overload, perfectionism, and difficulty stopping. The risk of Alzheimer's disease makes the finitude of memory salient and gives urgency to the act of leaving traces. The architecture responds to this double context with externalized memory, contracts, verification, and resumption.

The article makes four contributions. First, it offers a **moderate account of the cognitive prosthesis**, distinct from both the strong extended-mind thesis and the deflationary tool view. Second, it introduces the **cognitive signature** as an interpretive concept with explicit criteria of application, not as a biomarker or a literary flourish. Third, it develops an **epistemology of the prosthesis**, centered on the difference between coordination devices and epistemic warrants, and on the virtue of institutionalized epistemic humility. Fourth, it proposes an **ethics of self-design**, centered on care, epistemic inequality, and contestability. The article also responds to five objections, including the charge that the case is merely a personal knowledge management system and the charge that a self-study cannot support philosophical claims.

The method is a philosophical case study. It combines documentary analysis of the repository with the author's first-person report and with literature on extended cognition, cognitive artifacts, distributed cognition, epistemic dependence, and the ethics of care. It does not offer a clinical, neuropsychological, or experimental assessment. The health information is a self-report, not a diagnosis. The article does not claim that the system prevents, treats, or diagnoses Alzheimer's disease; it does not claim that giftedness causes Alzheimer's disease; and it does not offer medical advice. The case is illustrative, not representative: it is used to illuminate a phenomenon and to generate hypotheses, not to establish a general law.

The article proceeds as follows. Section 2 presents the case and the method. Section 3 asks what a cognitive prosthesis is and defends a moderate account. Section 4 examines authorship and the cognitive signature. Section 5 develops the epistemology of the prosthesis. Section 6 discusses the ethics of self-design. Section 7 responds to objections. Section 8 proposes an N-of-1 epistemology for testing claims about the prosthesis. Section 9 concludes.

## 2. The case and the method

### 2.1 The case

The Core is a public monorepo maintained by the author. In this article, “author” and “creator” refer to the same person, who designed the system and wrote this account. The local checkout analyzed on 10 November 2026 (Git base `1ce6ae98`) records 35 MCP servers, 35 commands, and 374 agent entries in `opencode.json`. The reconciled block in `README.md` records 366 agents and 35 MCPs; the divergence between counts is a reminder that an inventory is not a single portrait and that documentation also has a history. The repository contains 681 specification files in the `SPEC-*.md` pattern, 646 test files, and 845 evolution cycles. These are counts of files or configuration. None of them measures quality, availability, authentication, inference, or external validation.

The Core organizes operation around a six-move cycle: Perceive → Specify → Delegate → Execute → Verify → Reflect. The cycle is not a rigid sequence; it is a grammar of governance (Core Project, 2026b, 2026c). Each move has mechanisms, artifacts, and limits. The architecture includes a CLI, an orchestrator, a specification and test layer, a metacognitive memory layer, a trust and incentive layer, a catalog of agents, and a presentation and documentation layer. The details are described in the supplementary material; the philosophical argument requires only their functional role.

Three features of the Core matter for the argument. First, it **externalizes memory**: the MetaBus stores episodic and semantic memory, a confidence ledger, and events that can be consulted before a new decision. Second, it **externalizes verification**: specifications, tests, a SpecVerifier, a BehavioralGate, a metacognitive gate, and a public `CORRIGENDUM.md` govern the conditions under which a claim can be called verified. Third, it **externalizes the management of interruption**: the TaskRuntime assumes that a task can be interrupted and resumed, rather than demanding continuous presence. These features are not merely technical. They embody a normative stance: the system is designed as if memory could fail, conviction could deceive, and the person might need to stop.

### 2.2 Method

The article adopts the instrumental case study (Yin, 2018): the Core matters less for itself than for the phenomenon it illuminates — the construction of a cognitive prosthesis by its own user. The corpus includes:

- architecture and operation documents (`README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `MANUAL.md`, `CORRIGENDUM.md`);
- the R909 preface on cognitive signature and its specification;
- modules for memory, orchestration, verification, trust, economy, and evolution;
- evolution records and counts of specifications and tests;
- external literature on cognition, learning, giftedness, and dementia.

The analysis is documentary, not experimental. There was no execution of the system to measure performance, no cognitive testing of the author, and no access to medical records, biomarkers, or neuropsychological assessment. Claims about the code are verifiable in the cited files. Claims about the author's cognition are interpretations based on his self-report and his textual production, not diagnoses. The manuscript was prepared with AI assistance for preliminary drafting, structural editing, and reference formatting. The author reviewed, rewrote, and verified the text and takes full responsibility for the content. A detailed statement is provided in the Statements and Declarations.

### 2.3 Position and bias

The creator is also the main user of the system. This produces an advantage — access to the design process — and a risk: confirmation bias, the tendency to seek and interpret information in ways that support prior beliefs (Nickerson, 1998). The Core itself incorporates a response to this risk: the `CORRIGENDUM.md`, a public document of self-correction of claims; the metacognitive gate, which does not return “verified” without explicit external validation; and the requirement of specification, test, and receipt. These mechanisms do not eliminate bias. They make it visible and contestable — which is the most an architecture can promise.

### 2.4 Limits

The limits are explicit. First, this is a single case; it cannot be generalized to other people with giftedness, other creators, or other forms of neurocognitive risk. Second, there are no clinical data: the risk of Alzheimer's disease is reported, not diagnosed. Third, the counts are time-sensitive: specifications, tests, and cycles change with every commit. Fourth, the scores of the cycles are self-assessment, not an external benchmark (Core Project, 2026e). Fifth, no cognitive, functional, or clinical outcome was measured. Sixth, a metaphor is not a mechanism: calling modules “memory,” “attention,” or “metacognition” does not make them measures of the human mind (Poldrack, 2011). The boundary between description and diagnosis requires caution; the RDoC, for example, is a research framework, not a clinical instrument (Insel et al., 2010).

### 2.5 The situated case: giftedness and neurocognitive risk

Philosophical arguments about cognitive prostheses are often illustrated with hypothetical cases. This article uses a situated case, with all the limitations that entails. The author reports giftedness (high ability) and an elevated risk of Alzheimer's disease. The report is not a diagnosis, and it is not offered as a clinical fact. It is the background against which the design choices become intelligible.

Giftedness designates a profile of high potential, with heterogeneous manifestations in specific domains, combined with creativity and task commitment (Renzulli, 1978). Developmental models add that talent is built over time, in conditions of learning, support, and recognition (Gagné, 2004). In Brazil, educational law recognizes giftedness as a category of special education (Brasil, 1996, 2008), which confirms that it is an educational and developmental issue, not a pathology. The phrase “suffering from giftedness,” common in everyday speech, captures the distress that can accompany the asynchrony between capacity and environment, but it does not name a nosological category. The article uses the more precise formulation: the author reports giftedness.

The profile is associated, in the author's report, with systemic thinking, rapid pattern recognition, hyperfocus, and high standards. These are resources, but they also have costs: hyperfocus can erase the perception of time and basic needs; high standards can turn every delivery into a debt; associative speed can produce a sense of evidence that the data do not yet support. These costs are neither universal nor diagnostic. They are working hypotheses that explain why certain architectural choices appear in the Core: budgets, timeouts, checkpoints, specifications, tests, receipts.

The second element is the risk of Alzheimer's disease. It is important to distinguish three planes. **Alzheimer's disease** is, in contemporary research, defined by a biological continuum, with markers that can precede symptoms by decades (Jack et al., 2018). **Dementia** is a clinical syndrome with functional impact. **Risk** is a probabilistic estimate that combines genetics, vascular and metabolic factors, education, physical activity, hearing, social life, depression, and other factors (Livingston et al., 2020). Risk is not destiny; diagnosis is not prognosis; prognosis is not sentence.

The notion of **cognitive reserve** helps to think about the problem without promising miracles. The hypothesis is that life experiences — education, intellectual work, social engagement, complex activities — may allow a person to cope better with pathology before symptoms become disabling (Stern, 2002). This does not mean that a specific activity prevents the disease. The literature is observational, heterogeneous, and subject to reverse causation. No software has been validated as a neuroprotective intervention. A system like the Core can, at most, reduce environmental demands, support routines, externalize memory, and preserve continuity. These effects are plausible, but they need to be measured. The article treats them as research hypotheses, not results.

The combination of giftedness and neurocognitive risk is not a causal claim. There is no evidence that giftedness causes Alzheimer's disease, and the article does not speculate about such a link. The combination is a **design constraint**: it explains why a person with high cognitive demand and fear of loss would build a system to externalize memory, stabilize criteria, and make interruption survivable. The philosophical question is not whether the system cures or prevents anything. It is what kind of artifact such a response produces, and how it should be evaluated.

## 3. What is a cognitive prosthesis?

### 3.1 The extended mind thesis

Clark and Chalmers (1998) proposed that cognitive processes can extend beyond the skull. The classic example is Otto's notebook, which functions as a reliable and accessible external memory. The “parity principle” suggests that if an external process performs the same function as an internal one, it deserves the same cognitive status. The thesis is philosophical, not clinical: it shifts the unit of analysis from the brain to the person–environment system. On this view, a well-designed external memory is not a mere aid to cognition; it is part of the cognitive process itself.

The thesis has an intuitive appeal for the case at hand. The Core does not merely store information; it participates in the production of decisions. It holds the context that the author would otherwise have to reconstruct, the criteria that define what counts as done, and the records that make a claim contestable. If the extended mind thesis is right, the Core is not outside the author's cognition; it is one of its material conditions.

The lineage matters. Bush's (1945) memex and Engelbart's (1962) program for augmenting human intellect already imagined external systems that would help people think. The Core belongs to that lineage, but it adds a distinctive feature: it is not only a tool for storing or retrieving information; it governs the conditions under which a claim can be made, a task can be resumed, and a memory can be trusted.

### 3.2 The critics

The thesis also has serious critics. Rupert (2004) argues that extended cognition does not adequately explain the integration and persistence of internal processes. Sterelny (2010) proposes a more modest alternative: the mind is **scaffolded** by external structures, but not every scaffold becomes part of the cognitive system. Adams and Aizawa (2001) press a related point: the fact that an external process is coupled with an internal one does not show that the external process is constituted by the same kind of cognitive activity. Coupling is not constitution.

These objections matter for the case. The Core is coupled with the author's cognition in many ways: it stores his context, structures his tasks, and checks his claims. But coupling alone does not settle the metaphysical question. A notebook can be part of a cognitive process in one context and a mere object in another. The difference is not merely causal; it is normative. The notebook matters because it is trusted, consulted, and integrated into a practice. The same is true of the Core.

### 3.3 Cognitive artifacts and affordances

Norman (1991) showed that cognitive artifacts do not merely store information: they transform the task. A checklist is not a passive reminder; it reorganizes the sequence, reduces dependence on working memory, and makes error more visible. The same applies to a specification, an automated test, or a receipt with a hash. These artifacts do not “think” for the user; they change the economy of attention. Cognitive load theory explains why this matters: working memory is limited, and artifacts that reduce extraneous load free resources for the task (Sweller, 1988). Cognitive offloading is the general phenomenon of using the environment to reduce internal demand (Risko & Gilbert, 2016).

The Core is a cognitive artifact of a particular kind. It does not only represent what should be done; it defines **when** something can be considered done. It does not only store a result; it stores the evidence that makes the result contestable. This is the difference between a notebook and a system of governance. The notebook helps you remember; the Core helps you decide whether you are entitled to claim that you remember correctly.

### 3.4 Distributed cognition

Hutchins (1995) showed that the cognition of a cockpit is not only in the pilots' heads: it is distributed across people, instruments, procedures, and representations. Hollan, Hutchins, and Kirsh (2000) extended this approach to human–computer interaction. The unit of analysis is the coordinated system, not the isolated individual.

The Core is a distributed cognitive system: the author, the agents, the MCP servers, the specifications, the tests, and the records form a network that produces decisions. But there is an ethical asymmetry: only the author is accountable for what the system does. The distribution of cognition does not distribute responsibility. This asymmetry is the foundation of Section 4.

### 3.5 A moderate account

On the basis of these traditions, the article defends a **moderate account** of the cognitive prosthesis. The Core is not a literal part of the mind, but it is more than a neutral tool. It is a **robust scaffold** that satisfies three criteria:

1. **Load-bearing.** It carries part of the cognitive load: memory, sequencing, verification, and the management of interruption.
2. **Task-transforming.** It changes the affordances of the task, not merely the speed of execution. It makes certain errors visible, certain claims contestable, and certain forms of continuity possible.
3. **Normatively integrated.** It is embedded in practices of trust, verification, and care. The agent relies on it in a way that shapes their epistemic and practical agency.

The Core satisfies these criteria. It is load-bearing because the author would have to reconstruct context, criteria, and evidence without it. It is task-transforming because it turns a vague intention into a specification, a specification into a test, and a test into a contestable claim. It is normatively integrated because the author trusts it, corrects it, and depends on it. But none of this makes it a literal part of the mind. The concept of prosthesis is designed to capture this intermediate status: more than a tool, less than a constituent.

### 3.6 A taxonomy of cognitive prostheses

It is useful to distinguish four kinds of cognitive prosthesis:

1. **Storage prostheses** extend memory: notebooks, calendars, databases, and personal knowledge management systems.
2. **Procedural prostheses** extend executive function: checklists, workflows, task managers, and templates.
3. **Epistemic prostheses** extend verification and judgment: specifications, tests, evidence gates, peer review, and audit trails.
4. **Agentic prostheses** extend agency: systems that delegate tasks, execute actions, and coordinate multiple agents.

The Core is not just a storage prosthesis. It is an **agentic epistemic prosthesis**: it combines the capacity to delegate and execute with the capacity to verify and govern. This combination is what makes it philosophically interesting. A notebook can help you remember; a checklist can help you sequence; an agent can help you act. But a system that delegates, executes, and verifies raises a new question: who is accountable for the result? The answer cannot be “the system” alone, because the system does not have the kind of responsibility that accountability requires. The answer must be the human who designed the process and accepted the result, even if the causal contribution is distributed.

The taxonomy also clarifies the ethical stakes. Storage and procedural prostheses primarily raise questions of dependence and skill. Epistemic prostheses raise questions of trust and false objectivity. Agentic prostheses raise questions of agency and responsibility. The Core combines all four, which is why it is a demanding case: it concentrates the epistemic and ethical questions that are usually distributed across different technologies.

### 3.7 Why “prosthesis” is not a metaphor

The word “prosthesis” is not a metaphor. It is a functional analogy. A prosthesis replaces or supports a function that the person cannot perform, or cannot perform reliably, on their own. It has to fit the person, be maintained, and be integrated into a practice. It can restore agency, but it can also create dependence, discomfort, and new forms of vulnerability. The same is true of a cognitive prosthesis.

The analogy has limits. A medical prosthesis is typically prescribed by a professional and evaluated by clinical criteria. A cognitive prosthesis is often self-designed, self-fitted, and self-evaluated. This is precisely why the epistemology and ethics of self-design matter. The person who builds the prosthesis is also the person who uses it, and the person who evaluates it. The risk of overclaiming is built into the situation. The article's response is not to abandon the prosthesis, but to build practices that make overclaiming harder.

## 4. Authorship and the cognitive signature

### 4.1 The problem of composite authorship

The Core is not the product of a single mind. It uses libraries, models, data, inherited practices, and contributions from artificial agents. The author designed the architecture, chose the criteria, and wrote the specifications; the agents execute tasks, generate text, and propose solutions; the models are trained on corpora that no single person authored. Who, then, is the author of the system's outputs?

It is useful to distinguish four notions. **Causal contribution** is the broadest: many entities contribute to an output. **Agency** is the capacity to act and produce effects; an artificial agent can have agency in this thin sense. **Authorship** is the capacity to design the process, set the criteria, and decide what counts as a successful result; it is a normative capacity, not merely a causal one. **Responsibility** is the accountability for the consequences of the process; it is the capacity to answer for what was done.

The author has authorship and responsibility, even when the causal contribution is distributed. The agents have causal contributions and, in a thin sense, agency; they do not have authorship or responsibility in the relevant sense. This is not a denial of artificial agency. As Floridi and Sanders (2004) argue, artificial agents can be morally relevant without being moral persons. Nor is it a denial of distributed morality: as Floridi (2013) argues, moral responsibility can be distributed across a system of agents and artifacts. But distribution is not disappearance. The human remains the point at which accountability is located, because the human is the one who can be asked to justify the design, the criteria, and the decision to accept the result.

These distinctions matter for the cognitive signature. If authorship were reduced to causal contribution, the signature would be a collective product with no owner. If it were reduced to authorial control, the signature would be a purely mental intention with no material trace. The interesting case is in between: the signature is materialized in the architecture, but it is not exhausted by the author's intentions. It is a **style of responsibility** that emerges from the interaction between the author, the agents, and the artifacts.

### 4.2 The cognitive signature

The project's design preface defines the **authored cognitive signature** as “this situated configuration of documentable choices” (Core Project, 2026a). The definition is deliberately modest. It does not claim that code reveals the author's mind; it claims that code preserves marks of the author's questions, criteria, representations, and decisions. The strong version — that any given ecosystem would reveal, in a unique and recoverable way, the cognition of a single creator — exceeds the available evidence. Stylistic attribution from technical artifacts has limits; it can preserve regularities, but it does not measure personality or cognition (Caliskan et al., 2018).

The concept has four criteria of application. First, **documentability**: the choices must be observable in the artifact, not merely inferred from the author's testimony. Second, **recurrence**: the choices must appear across contexts, not in a single isolated decision. Third, **counterevidence**: the interpretation must be contestable by choices that contradict the pattern. Fourth, **explanatory power**: the signature must explain something about the system's behavior that would otherwise be puzzling. These criteria do not make the signature a scientific measurement. They make it an interpretive hypothesis with public constraints.

### 4.3 Five marks

Five marks are documentable in the Core. They do not exhaust the signature; they are an interpretive cut.

**1. Memory treated as fragile.** The system is built as if memory could fail. There is shared memory, a confidence ledger, specifications, receipts, hashes, state anchors. This choice is not only technical: it is an existential stance. The design does not trust remembrance; it trusts the record. The sentence “what was executed, with which source, which hash, and which limit?” is a response to the possibility of forgetting.

**2. The contract before the impulse.** The rule “no delivery without a specification” subordinates inspiration to a form. For a creator with high fluency and hyperfocus, this is counterintuitive: the will to make comes before the contract. The architecture inverts the order. The contract does not deny the impulse; it protects it from itself, preventing enthusiasm from redefining the criterion of success halfway through.

**3. Verification against one's own conviction.** The anti-overclaim gate, the `CORRIGENDUM.md`, and the requirement of external validation are a response to the tendency to confuse coherence with truth. This is perhaps the most distinctive mark of the Core. It is not about distrusting others; it is about distrusting one's own capacity to build a convincing narrative. The architecture turns that distrust into procedure.

**4. The architecture of interruption.** The runtime assumes that the task can be interrupted; the MetaBus assumes that context can be lost; the `doctor` assumes that the environment can be broken. The system is made to resume, not to demand continuous presence. This mark is especially significant in a context of neurocognitive risk: the architecture does not promise perfect memory, but it promises a way back.

**5. The didactic vocation.** The book, the manual, MIRA, the explainers, and the concern with the “democratization of knowledge” show that the signature is not only in the code. It is in the will to teach what was learned. This mark has an ethical dimension: knowledge is not treated as property, but as something that should be made accessible — with limits, sources, and warnings.

**Table 1. Five marks of the cognitive signature**

| Mark | Evidence in the Core | Interpretation | Counterevidence |
|---|---|---|---|
| Memory treated as fragile | MetaBus, hashes, receipts, state anchors | Distrust of remembrance; trust in the record | The system keeps only the last 1,000 events |
| Contract before impulse | Specs, acceptance criteria, TDD | Protection of intention against volatility | A spec can become bureaucracy |
| Verification against conviction | Anti-overclaim gate, `CORRIGENDUM.md` | Distrust of coherent narratives | Self-assessment remains self-assessment |
| Architecture of interruption | DAGs, leases, checkpoints, resumption | Design for fatigue and loss of context | The user can still overwork |
| Didactic vocation | Book, manual, MIRA, explainers | Knowledge as a common good | Documentation is not pedagogical efficacy |

### 4.4 The signature as a style of responsibility

The signature is not a fingerprint. It is a **style of responsibility**: a characteristic way of responding to uncertainty. The author responds to uncertainty by documenting, testing, correcting, and asking for review. This is not a psychological trait; it is a normative posture materialized in the architecture. The same posture could be adopted by someone with a different personality, and the same personality could produce a different posture. The signature is the posture, not the person. The “mirroring” hypothesis suggests that the modularity of a system can reflect the coordination style of those who produce it (MacCormack et al., 2012). This supports a composite reading of the signature: it is not a portrait of the author, but the result of an interaction among author, tools, models, and community.

This has an important consequence for the ethics of AI. If the signature is a style of responsibility, then the relevant question is not “who is the author?” in a metaphysical sense, but “who is accountable?” in a practical sense. The human who designs the process and accepts the result is accountable, even if the output is co-produced by agents. The agents can be causally relevant without being responsible. The signature is the trace of that accountability.

### 4.5 The risk of myth

Every interpretation of authorship runs the risk of becoming myth. The myth has three forms. The first is **celebration**: turning the architecture into proof of genius. The second is **justification**: using the signature to explain or excuse failures. The third is **prison**: believing that the author can only create in one way, and that the signature is a destiny.

The article refuses all three. The signature is an interpretive hypothesis, not an essence. Generalization from a single case requires caution (Yarkoni, 2022). It can be contested by counterexamples: choices that contradict the pattern, contributions that come from others, moments when the system fails. The very existence of the `CORRIGENDUM.md` is a counterproof to the temptation to celebrate. A system that corrects itself publicly is not a monument; it is a work in progress.

## 5. The epistemology of the prosthesis

### 5.1 Externalized memory

The MetaBus is described as a “unified metacognitive event bus” and a “shared memory” among agents. It maintains episodic memory, semantic memory, and a **confidence ledger** — a record of confidence by agent or topic. The declared inspiration is Global Workspace Theory, the Reflexion framework (Shinn et al., 2023), and collaborative memory in multi-agent systems (Core Project, 2026f). In practice, the MetaBus publishes events, allows agents to subscribe to them, and persists a state that can be consulted before a new decision. Memory is selective: the code keeps the last 1,000 episodic events. This is a design choice, not a detail. A system that tried to remember everything would have cost, noise, and risk of contamination. Selectivity is a form of productive forgetting.

The externalized cognitive function is **context**. The author does not need to reconstruct from memory what has already been decided, tested, or discarded. But the MetaBus is not a backup of the mind. It records traces, not lived experience. The difference matters: a trace can be consulted; an experience must be interpreted. The risk is that the record comes to seem more complete than it is. A selective memory can produce a false sense of continuity. The author may remember the record and forget the gaps.

### 5.2 Verification

Verification is the epistemic heart of the Core. The TDDRunner produces test evidence; the SpecVerifier checks criteria; the BehavioralGate authorizes or blocks actions based on trust; the metacognitive gate classifies the degree of a claim and **does not return “verified” without explicit external validation**. The `CORRIGENDUM.md` records claims that sounded stronger than the available evidence and proposes the correct reading. The practice of writing the test before the implementation is the basis of TDD (Beck, 2002).

The externalized cognitive function is **reality testing**. The system does not prevent the author from believing something; it makes it harder to declare that something has been proven when it has not. For someone with a high capacity to build coherent narratives, this is a necessary counterweight. The internal coherence of an explanation is not proof of its truth; a test that passes is not proof that the test measures what it should measure; a high score is not proof of merit.

The limit is the same as that of any verification system: it only verifies what has been specified. A test can confirm a wrong hypothesis, a specification can formalize an inadequate criterion, a gate can block a correct action. Verification is a practice, not a certainty machine. The literature on reproducibility shows that apparent results may not hold (Ioannidis, 2005). The Core's response is not to claim certainty, but to institutionalize the possibility of correction.

### 5.3 Trust and false objectivity

The Blackboard implements a shared board on which agents volunteer for tasks based on **Agent Cards** — descriptions of capabilities, input schema, and status. The blackboard pattern is classic in AI systems (Nii, 1986), and the notion of an agent as an autonomous system that perceives and acts in an environment comes from the agent literature (Wooldridge & Jennings, 1995). Selection weighs declared capabilities, historical confidence, and load. The Trust Engine maintains scores by action, applies a behavioral gate, and records outcomes. The Token Economy adds stake, slashing, and a fee market (Core Project, 2026f).

There are two risks. The first is **false objectivity**: a confidence score is not a measure of truth. An agent can have high trust and produce a wrong answer with confidence. The second is **false merit**: stake measures commitment, not competence. The token economy is a coordination device, not an epistemology. The same is true of the trust score. It is useful for allocating attention and tasks; it is not a warrant for belief. The moment a coordination device is treated as an epistemic warrant, the prosthesis becomes a machine for producing false confidence. Two further risks follow from this. **Automation bias** is the tendency to accept an agent's output because it is fluent and confident, even when the evidence is weak. **Deskilling** is the loss of the capacities that the prosthesis was meant to support: memory, judgment, and verification. Both are epistemic risks, not merely practical ones. They are the price of offloading, and they must be monitored rather than denied.

### 5.4 Epistemic dependence

The Core does not eliminate epistemic dependence; it redistributes it. The author depends on agents, models, records, and the architecture itself. This is not a defect. All cognition is epistemically dependent, in the sense that it relies on others, on institutions, and on artifacts (Hardwig, 1985). The question is whether the dependence is **accountable**. Can the author trace the source of a claim? Can he contest it? Can he exit the system? Can he tell when the system is wrong?

The difference between trusting a person, a tool, and a system is important. Trusting a person involves attributing competence and honesty; trusting a tool involves relying on its causal reliability; trusting a system involves relying on a network of people, artifacts, and procedures. The Core is a system in this sense. Its trustworthiness is not a property of a single component; it is a property of the whole arrangement. This is why the architecture of verification matters. It is not enough for the system to be reliable; it must be **contestable**.

Hardwig (1985) argues that epistemic dependence is not a failure of rationality but a condition of it. We cannot verify everything ourselves; we rely on experts, institutions, and testimony. The Core generalizes this dependence to artifacts and agents. The question is not whether to depend, but how to make dependence accountable. This requires distinguishing **trust** from **reliance**. Reliance is a causal expectation: I expect the system to work. Trust is a normative attitude: I expect the system to be worthy of reliance, and I am willing to be answerable for that expectation. The Core invites both. Its tests and gates are designed to make reliance more reliable; its corrigendum and external validation are designed to make trust more contestable. The risk is to conflate the two — to treat a reliable system as a trustworthy one, or a trustworthy one as infallible.

### 5.5 Epistemic humility as a design virtue

The Core's most distinctive epistemic feature is not its capacity to verify, but its capacity to refuse. The metacognitive gate does not return “verified” without external validation. The `CORRIGENDUM.md` records the system's own overclaims. The design assumes that the author can be wrong, that the agents can be wrong, and that the tests can be wrong. This is a form of **institutionalized epistemic humility**.

Humility, here, is not a feeling. It is a set of practices: documenting sources, distinguishing levels of evidence, inviting criticism, and correcting in public. The Core materializes some of these practices. It does not guarantee that the author will be humble; it makes humility easier to enact and harder to fake. This is the sense in which the prosthesis can be an epistemic virtue: not because it makes the person virtuous, but because it structures the practice in which virtue can be exercised.

## 6. The ethics of self-design

### 6.1 Care and dependency

The prosthesis can become a **second disease**. A system that demands specs, tests, reviews, updates, and maintenance can consume the life it was supposed to protect. The author can spend more time caring for the architecture than living what the architecture should make possible. Hyperfocus, which is a strength, can ally itself with perfectionism and turn the Core into a labyrinth. The repository has 681 specs, 646 tests, and 845 cycles. The wealth is real; the cost is also real.

The ethics of care is relevant here. Care is not only about helping; it is about sustaining the conditions in which the other can flourish without being absorbed by the help (Tronto, 1993). A prosthesis that demands constant attention is not care; it is a new form of burden. The result is a **bureaucratization of care**: the system demands documentation, maintenance, and justification, and the person becomes an administrator of his own support. The architecture needs **stop rules** — explicit criteria for stopping, publishing, resting, and leaving something imperfect. It also needs **humane defaults**: when the system fails, it should offer an explanation, an alternative, a human contact, a way to continue. The architecture of verification needs to be accompanied by an architecture of care.

Tronto (1993) distinguishes four phases of care: attentiveness (noticing a need), responsibility (taking on the obligation to meet it), competence (having the capacity to meet it), and responsiveness (responding to the other's response). The Core can support attentiveness and responsibility: it records needs, tasks, and commitments. But it can also distort them. It can make the author attentive to the system's needs rather than his own; it can make him responsible for maintaining the system rather than for his own care. A prosthesis that consumes the caregiver is not a practice of care. The architecture should be judged by the same criteria: does it help the author notice his needs, take responsibility for them, meet them competently, and respond to his own limits?

### 6.2 Epistemic inequality

Cognitive prostheses are not equally accessible. They require hardware, energy, time, technical knowledge, and a certain freedom to experiment. The Core's MIT license, local-first emphasis, and open documentation are partial responses to this inequality. They do not solve it. A person who cannot afford the hardware, or who does not have the time to build and maintain the system, is excluded from the benefits.

This is a question of **epistemic injustice** (Fricker, 2007). The distribution of cognitive prostheses can reinforce existing inequalities in access to knowledge, health, and care. The open-source model can mitigate the problem, but it can also create a new divide between those who can build and those who can only consume. The ethical task is not only to make the prosthesis available; it is to make it **adaptable**, **maintainable**, and **contestable** by the people who need it.

### 6.3 The ethics of self-experimentation

The author is both researcher and subject. The N-of-1 protocol proposed in Section 8 is an attempt to test the prosthesis without overclaiming. But self-experimentation raises ethical questions. Who protects the subject? Who interprets the results? Who decides when to stop? The person who builds the prosthesis is not in a good position to evaluate it alone. The protocol therefore requires pre-registration, clinical oversight, and independent review. The fact that the intervention is personal does not make ethical safeguards less necessary; it makes them more necessary.

### 6.4 Contestability

The prosthesis must be open to criticism, reproduction, and modification. The “house” must have doors. Technological mediation materializes values and choices, but it does not guarantee that they are virtuous (Verbeek, 2006). This is why contestability matters: the artifact can embody a good intention and still produce a bad effect. A system that can only be understood by its creator is not a contribution to knowledge; it is a private language. The Core's documentation, tests, and public correction are attempts to keep the doors open. They are not enough. The ultimate test of the prosthesis is whether someone else can use it, question it, and change it.

## 7. Objections and replies

### 7.1 “This is just a personal knowledge management system”

**Objection.** The Core is a collection of notes, tasks, and scripts. Calling it a cognitive prosthesis inflates a familiar practice into a philosophical thesis.

**Reply.** The difference is not the presence of notes, but the **normative architecture** that governs them. A personal knowledge management system helps you store and retrieve information. The Core governs the conditions under which a claim can be called verified, a task can be resumed, and a memory can be trusted. It includes specifications, tests, a verifier, a behavioral gate, a public corrigendum, and a metacognitive gate that refuses “verified” without external validation. These are not storage features; they are epistemic procedures. The concept of prosthesis is meant to capture this difference. It is a functional concept, not a metaphysical one.

### 7.2 “The extended mind thesis is false; the Core is just a tool”

**Objection.** The extended mind thesis has been criticized on metaphysical grounds. If the thesis is false, the Core is a tool, and the language of prosthesis is misleading.

**Reply.** The article does not rely on the strong extended-mind thesis. It adopts a **moderate account**: the Core is a robust scaffold that transforms the task and redistributes epistemic labor, but it does not constitute the mind. This account is compatible with the critics. Rupert (2004) and Sterelny (2010) are right that coupling is not constitution. But the normative significance of the prosthesis does not depend on constitution. A tool can be load-bearing, task-transforming, and normatively integrated without being a part of the mind. The concept of prosthesis is designed to occupy this intermediate space.

### 7.3 “The cognitive signature is not empirically testable”

**Objection.** The cognitive signature is a literary interpretation. It cannot be measured, falsified, or generalized. It is not a scientific concept.

**Reply.** The signature is not a biomarker, and it is not intended to be. It is an interpretive hypothesis with public constraints: documentability, recurrence, counterevidence, and explanatory power. These constraints do not make it a measurement, but they make it contestable. The signature can be assessed in the same way as other interpretive claims in interpretive social science and the humanities: by coherence, explanatory power, and openness to counterevidence. The article does not claim that the signature is a natural kind. It claims that it is a useful concept for understanding how values and choices are materialized in artifacts.

### 7.4 “The self-study is biased and cannot support philosophical claims”

**Objection.** The author is the creator and the user of the system. The case is subjective, selective, and self-serving. It cannot support a general philosophical argument.

**Reply.** The case is instrumental, not representative. It is used to illuminate a phenomenon and to generate hypotheses, not to establish a general law. The biases are disclosed, and the system itself incorporates mechanisms that make some biases visible: the public corrigendum, the anti-overclaim gate, the requirement of external validation. These mechanisms do not eliminate bias, but they make the case more contestable than a purely autobiographical account. The article also invites counterexamples and independent review. A self-study can be a legitimate philosophical method if it is conducted with appropriate humility and transparency.

### 7.5 “Using AI to write about AI-authored cognition is circular”

**Objection.** The article was drafted with an AI assistant. Using AI to analyze a system that uses AI is circular. The argument undermines itself.

**Reply.** The AI is a tool, not an author. The author designed the argument, selected the sources, verified the claims, and takes responsibility for the text. The use of AI is disclosed in the method and in the declarations. The circularity is not a flaw in the argument; it is part of the case. The article is about the conditions under which humans and agents co-produce cognition. Writing about that condition with the help of an agent is not a refutation; it is an illustration. The relevant question is whether the human remains accountable. The article argues that he does.

## 8. Testing the hypothesis: an N-of-1 epistemology

The claim that the prosthesis helps is an empirical hypothesis. It should be tested, not presumed. The case is unique, personalized, and heterogeneous; a traditional randomized trial is neither feasible nor ethical. The N-of-1 design — or single-case experiment — allows hypotheses to be tested in one person, with repeated measures, alternated conditions, and pre-registration (Nosek et al., 2018). It does not produce statistical generalization, but it produces local evidence, useful for informed decisions.

The protocol is a proposal. It was not executed. It should be adapted with health professionals, neuropsychologists, and research ethics review. The primary outcomes should include time to resume after an interruption, task completion rate, error rate in routine tasks, perceived cognitive load, and calibration of trust. Secondary outcomes should include sense of agency, sleep and social life, and stress symptoms. The full outcome matrix is provided in the supplementary material.

A possible design is an **ABAB with randomized blocks** over 12 weeks. In phase A, the author performs comparable tasks with his usual tools, without the system. In phase B, he uses the system with the same tasks. A and B alternate, with a one-week washout. The order of blocks is randomized and recorded. The evaluation of some outcomes can be blinded. Hypotheses, outcomes, analyses, and stopping criteria are registered before the start. The analysis can combine visual inspection of time series with mixed models; effect sizes should be reported with uncertainty; multiplicity should be controlled or explicitly discussed; negative results should be published. The analysis should not be performed by the same agent that implemented the intervention without independent supervision.

The ethics of the protocol are as important as its design: informed consent, protection of sensitive data, clinical supervision, separation between research and care, review by an ethics committee when applicable, and a commitment not to turn the result into a claim of cure or prevention. The N-of-1 protocol is not a concession to empiricism. It is an expression of the same epistemic humility that the Core tries to institutionalize: the willingness to treat one's own prosthesis as a hypothesis.

## 9. Conclusion

This article analyzed the Core as an authored cognitive prosthesis. The argument proceeded in three steps. First, the system is a robust scaffold that carries part of the cognitive load, transforms the task, and is normatively integrated into the author's practices. It is not a literal part of the mind, but it is more than a neutral tool. Second, its cognitive signature is a situated configuration of documentable choices — a style of responsibility, not a fingerprint. Third, the ideal of epistemic sovereignty that motivates the system is necessarily limited: the prosthesis manages dependence on agents, models, and records, but it cannot eliminate it.

The context of giftedness and risk of Alzheimer's disease gives urgency to the project. Giftedness helps to explain the intensity, the complexity, and the demand for rigor; neurocognitive risk helps to explain the emphasis on memory, continuity, and resumption. But the article refused easy causality: there is no evidence that giftedness causes Alzheimer's disease, nor that the Core prevents the disease. What exists is a coherence of design: a system built to sustain the cognitive life of someone who knows his own fragility.

The main contribution is not the system itself, but the possibility of thinking about it critically. An authored cognitive prosthesis should be evaluated by what it preserves, not by what it promises. If the Core helps the author continue thinking, working, and teaching, it fulfills a function; if it prevents him from sleeping, from socializing, or from stopping, it fails. The criterion is not the number of agents, specs, or cycles. It is the quality of life that the architecture makes possible.

The research program that opens is clear: to measure, with an N-of-1 design and clinical supervision, the effects of the Core on resumption, cognitive load, errors, agency, and well-being; to compare it with simpler alternatives; to investigate the risks of dependency and deskilling; and to develop an ethics of cognitive prostheses that is both rigorous and humane.

The house does not replace the architect. It gives him back time and space to continue designing — and, when necessary, to leave.

---

## Statements and Declarations

**Competing interests.** The author declares no competing financial or non-financial interests. The author is the creator and main user of the system analyzed in this article. This relationship is disclosed here and is treated as a potential source of bias in Section 2.3.

**Funding.** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

**Ethics approval and consent to participate.** This is a self-study based on documentary analysis of the author's own software project and on the author's self-report. It does not involve human participants other than the author, and no clinical, biometric, or identifiable third-party data were used. Ethical approval was therefore not required. The author consents to the publication of the self-report and of the analysis.

**Consent for publication.** The author is the sole participant and consents to publication.

**Data and code availability.** The code, specifications, tests, and evolution records are available in a public repository. The repository URL is withheld from the anonymized manuscript for double-blind review and is provided on the title page. The article does not report experimental data; the documentary corpus is described in Section 2.2.

**Preprint.** An earlier, Portuguese-language version of this article is available in the project's public repository. It has not been peer-reviewed. The present manuscript is a substantially revised and translated version.

**Use of AI.** The author used an AI assistant (an orchestrator based on DeepSeek V4.1 Flash, via OpenCode) for preliminary drafting, structural editing, and reference formatting. The author reviewed, rewrote, and verified the text, verified the sources, and takes full responsibility for the content. The AI is not an author and did not make interpretive or ethical decisions. A detailed account of the human–AI division of labor is provided in the title page.

**Author contributions.** The author conceived the study, designed the system, collected the documentary evidence, wrote and revised the manuscript, and approved the final version.

**Acknowledgements.** The author thanks the open-source communities whose libraries, models, and tools made the Core possible. The author also thanks the reviewers, whose criticism will improve the argument.

---

## References

Adams, F., & Aizawa, K. (2001). The bounds of cognition. *Philosophical Psychology, 14*(1), 43–64. https://doi.org/10.1080/09515080120033571

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

Floridi, L. (2013). Distributed morality in an information society. *Science and Engineering Ethics, 19*(3), 727–743. https://doi.org/10.1007/s11948-012-9413-4

Floridi, L., & Sanders, J. W. (2004). On the morality of artificial agents. *Minds and Machines, 14*(3), 349–379. https://doi.org/10.1023/B:MIND.0000035461.63578.9d

Fricker, M. (2007). *Epistemic injustice: Power and the ethics of knowing*. Oxford University Press.

Gagné, F. (2004). Transforming gifts into talents: The DMGT as a developmental theory. *High Ability Studies, 15*(2), 119–147. https://doi.org/10.1080/1359813042000314682

Hardwig, J. (1985). Epistemic dependence. *The Journal of Philosophy, 82*(7), 335–349. https://doi.org/10.2307/2026523

Hollan, J., Hutchins, E., & Kirsh, D. (2000). Distributed cognition: Toward a new foundation for human-computer interaction research. *ACM Transactions on Computer-Human Interaction, 7*(2), 174–196. https://doi.org/10.1145/353485.353487

Hutchins, E. (1995). *Cognition in the wild*. MIT Press.

Insel, T., Cuthbert, B., Garvey, M., Heinssen, R., Pine, D. S., Quinn, K., Sanislow, C., & Wang, P. (2010). Research domain criteria (RDoC): Toward a new classification framework for research on mental disorders. *American Journal of Psychiatry, 167*(7), 748–751. https://doi.org/10.1176/appi.ajp.2010.09091379

Ioannidis, J. P. A. (2005). Why most published research findings are false. *PLoS Medicine, 2*(8), e124. https://doi.org/10.1371/journal.pmed.0020124

Jack, C. R., Bennett, D. A., Blennow, K., Carrillo, M. C., Dunn, B., Haeberlein, S. B., Holtzman, D. M., Jagust, W., Jessen, F., Karlawish, J., Liu, E., Molinuevo, J. L., Montine, T., Phelps, C., Rankin, K. P., Rowe, C. C., Scheltens, P., Siemers, E., Snyder, H. M., & Sperling, R. (2018). NIA-AA research framework: Toward a biological definition of Alzheimer's disease. *Alzheimer's & Dementia, 14*(4), 535–562. https://doi.org/10.1016/j.jalz.2018.02.018

Livingston, G., Huntley, J., Sommerlad, A., Ames, D., Ballard, C., Banerjee, S., Brayne, C., Burns, A., Cohen-Mansfield, J., Cooper, C., Costafreda, S. G., Dias, A., Fox, N., Gitlin, L. N., Howard, R., Kales, H. C., Kivimäki, M., Larson, E. B., Ogunniyi, A., … Mukadam, N. (2020). Dementia prevention, intervention, and care: 2020 report of the Lancet Commission. *The Lancet, 396*(10248), 413–446. https://doi.org/10.1016/S0140-6736(20)30367-6

MacCormack, A., Baldwin, C., & Rusnak, J. (2012). Exploring the duality between product and organizational architectures: A test of the mirroring hypothesis. *Research Policy, 41*(8), 1309–1324. https://doi.org/10.1016/j.respol.2012.04.011

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

Tronto, J. C. (1993). *Moral boundaries: A political argument for an ethic of care*. Routledge.

Verbeek, P.-P. (2006). Materializing morality: Design ethics and technological mediation. *Science, Technology, & Human Values, 31*(3), 361–380. https://doi.org/10.1177/0162243905285847

Wooldridge, M., & Jennings, N. R. (1995). Intelligent agents: Theory and practice. *The Knowledge Engineering Review, 10*(2), 115–152. https://doi.org/10.1017/S0269888900008122

Yarkoni, T. (2022). The generalizability crisis. *Behavioral and Brain Sciences, 45*, e1. https://doi.org/10.1017/S0140525X20001685

Yin, R. K. (2018). *Case study research and applications: Design and methods* (6th ed.). Sage.

---

## Supplementary material

**Supplementary Table S1.** Repository indicators (10 November 2026; Git base `1ce6ae98`). Counts of specification files, test files, evolution cycles, configured agents, MCP servers, commands, and structural checks, with the corresponding limits of interpretation.

**Supplementary Table S2.** Cognitive functions and architectural mechanisms: move, externalized function, mechanism, evidence, and limit.

**Supplementary Table S3.** From reported vulnerability to architectural hypothesis: vulnerability, design hypothesis, mechanism, and limit.

**Supplementary Table S4.** Proposed N-of-1 outcome matrix: outcome, instrument, frequency, hypothesis, and risk of distortion.

**Supplementary Note S1.** Glossary of architectural terms: MetaBus, Blackboard, Agent Card, Trust Engine, BehavioralGate, TaskRuntime, SpecRegistry, SpecVerifier, EvolutionRegistry, and Token Economy.

**Supplementary Note S2.** Anonymized inventory of the documentary corpus and file paths used in the analysis.
