---
title: "Thucy: An LLM-based Multi-Agent System for Claim Verification across Relational Databases"
authors:
  - "Michael Theologitis"
  - "Dan Suciu"
year: 2025
venue: "arXiv"
source: arxiv
pdf: [2025] - thucy-an-llm-based-multi-agent-system-for-claim-verification-across-re.pdf
converted_by: opencode-ecosystem-core/research
---

Thucy: An LLM-based Multi-Agent System for Claim Verification across
                                                                    Relational Databases
                                                                                         Michael Theologitis1 , Dan Suciu1
                                                                                                  1
                                                                                               University of Washington
                                                                               Paul G. Allen School of Computer Science & Engineering
                                                                                          {mthe, suciu}@cs.washington.edu


                                                                    Abstract                                      It turns out, the City of Seattle publicly provides an offiarXiv:2512.03278v2 [cs.DB] 5 Jan 2026


                                                                                                              cial crime dataset (Seattle Police Department 2025b)—with
                                          In today’s age, it is becoming increasingly difficult to de-
                                                                                                              all crimes from 2008 until now—that is structured, detailed,
                                          cipher truth from lies. Every day, politicians, media outlets,
                                          and public figures make conflicting claims—often about top-         and updated almost daily. In principle, that is all you would
                                          ics that can, in principle, be verified against structured data.    need to verify such a claim. In practice, though, very few
                                          For instance, statements about crime rates, economic growth         people ever try. Most will simply take the statement at face
                                          or healthcare can all be verified against official public records   value and move on, keeping the comforting thought that
                                          and structured datasets. Building a system that can automat-        “Seattle is safer now” somewhere in the back of their mind.
                                          ically do that would have sounded like science fiction just a           A few more curious and determined souls might go a step
                                          few years ago. Yet, with the extraordinary progress in LLMs         further, dig around, discover the dataset, and even download
                                          and agentic AI, this is now within reach. Still, there remains      it. Then reality hits: it is technical, messy, and not exactly
                                          a striking gap between what is technically possible and what
                                                                                                              friendly to non-specialists. So they, too, eventually give up.
                                          is being demonstrated by recent work. Most existing verifica-
                                          tion systems operate only on small, single-table databases—         And so the claim remains—unchecked, unchallenged, and
                                          typically a few hundred rows—that conveniently fit within an        protected by the technical complexity of verification.
                                          LLM’s context window.                                                   In this work, we present a multi-agent system called
                                          In this paper we report our progress on T HUCY, the first           T HUCY that takes over the verification process once the user
                                          cross-database, cross-table multi-agent claim verification sys-     has obtained the structured data and imported it into a re-
                                          tem that also provides concrete evidence for each verification      lational database. From that point on, T HUCY figures ev-
                                          verdict. T HUCY remains completely agnostic to the under-           erything out: it autonomously explores the available data
                                          lying data sources before deployment and must therefore au-         sources, reasoning over them on the fly to produce a verdict
                                          tonomously discover, inspect, and reason over all available re-     and supporting evidence.
                                          lational databases to verify claims. Importantly, T HUCY also
                                                                                                                  In our example, we can simply download the City of Seat-
                                          reports the exact SQL queries that support its verdict (whether
                                          the claim is accurate or not) offering full transparency to ex-     tle’s official crime dataset, load it into a SQL database, and
                                          pert users familiar with SQL. When evaluated on the TabFact         invoke T HUCY with the verbatim claim of Ann Davison for
                                          dataset—the standard benchmark for fact verification over           verification. T HUCY takes care of the rest—no further clari-
                                          structured data—T HUCY surpasses the previous state of the          fications are needed. In fact, T HUCY is completely agnostic
                                          art by 5.6 percentage points in accuracy (94.3% vs. 88.7%).         to the underlying data environment before deployment.
                                                                                                                  We draw inspiration from the work of Thucy(dides), the
                                        Code — https://github.com/michaeltheologitis/thucy                    Athenian historian (460–400 BC) who wrote the History of
                                                                                                              the Peloponnesian War between Sparta and Athens. “Thucy-
                                                                                                              dides has been dubbed the father of scientific history by
                                                              1    Introduction                               those who accept his claims to have applied strict standards
                                        In the Annual Report released last year by the Seattle City           of impartiality and evidence-gathering” (Wikipedia 2025).
                                        Attorney’s Office (2024), we read the following:                          Following Thucydides’ example of reporting, T HUCY’s
                                           I am pleased to acknowledge that 2024 saw a reduc-                 job is twofold: 1 provide a verification verdict (whether the
                                           tion in property crime and violent crime in Seattle.               claim is supported or not based on the available data), and
                                           — Ann Davison, City Attorney                                        2 return a report together with SQL queries that explain its
                                                                                                              findings. By returning the explanations in the form of SQL
                                        However, for many residents of Seattle, this statement might
                                                                                                              queries, T HUCY empowers the data analyst to modify these
                                        not quite match their lived experience. The natural instinct
                                                                                                              SQL queries and explore the claim further. For example they
                                        is to want to find out more. Was crime really down in 2024?
                                                                                                              can “roll-up” by checking if crime of all types has decreased
                                        And if so, by how much—and according to which source?
                                                                                                              in Seattle in 2024 (not just property and violent crime), or to
                                        Copyright © 2026, Association for the Advancement of Artificial       “drill down” and check how crime changed in 2024 for each
                                        Intelligence (www.aaai.org). All rights reserved.                     Seattle neighborhood.
                                       Data Expert


             Verifier                Schema Expert


                                       SQL Expert


Figure 1: The architecture of T HUCY, a multi-agent system led by the Verifier. Its job is to verify NL claims grounded in
relational databases and report the corresponding SQL evidence. The Verifier coordinates three expert agents: the Data Expert,
which summarizes available data sources; the Schema Expert, which answers schema-related questions; and the SQL Expert,
which writes and executes SQL queries to obtain verifiable answers. The data layer follows a plug-and-play design and can
include any number of relational databases—each potentially containing many tables—with PostgreSQL, MySQL, SQL Server,
and Oracle shown here only as examples. T HUCY remains fully agnostic to the underlying data sources. The agents must
therefore operate in an open-ended environment, discovering and reasoning about available data as they encounter it. The
experts interact with these relational databases through specialized tools managed via Google’s MCP Toolbox. Adding or
removing databases is straightforward: it simple involves adding or removing the corresponding tool from the toolbox.


                    2   Architecture                              quickly plug-and-play by adding or removing data sources
In this section, we describe the architecture of T HUCY. We       without concern for compatibility or reconfiguration. This
start by discussing the data sources and our minimal assump-      flexibility has been a central motivation since the inception
tions about them. Then, we go over the recent standardized        of our system.
ways modern AI agents connect to databases. Finally, we
delve into the details of our multi-agent system (Figure 1).      Tools
   Throughout this section, we aim to be as informative as        To enable this flexibility, we must address a fundamental
possible about the unique ways multi-agent systems must           challenge: LLMs, no matter how capable, are inherently disnavigate relational databases. Table 1 summarizes, at a high      connected from external data sources—they can only oplevel, how T HUCY differs from prior systems that operate         erate in isolation, with no way to interact with databases.
over structured data. Beyond explaining how our system            Agents bridge this gap by using tools. A tool acts as an interworks, our goal is to also make clear the rationale behind the    face to external capabilities, allowing agents to interact with,
design choices that made T HUCY possible. Doing so natu-          perceive, and affect their environment. In general, tools can
rally requires unpacking some of the subtleties of relational     include capabilities that perform mathematical calculations,
databases along the way.                                          or read files from disk, or query a database. Each agent has
                                                                  a fixed collection of such tools. At runtime, the agent1 auData Sources                                                      tonomously decides which tool to invoke, how to call it, and
                                                                  when to use it; the tool’s output is then fed back into the
The vision behind T HUCY is simple. A user can drop a few         reasoning loop (Yao et al. 2023). This interactive feedback
grounding data sources into SQL databases and immedi-             cycle between reasoning, action, and observations forms the
ately start asking the system to verify claims. We make only      backbone of modern agentic AI.
minimal assumptions about these data sources: they are re-           Building tools from scratch is challenging, because they
lational—as is often the case with official federal or state      need to be carefully designed. They must return well formatdata—and we treat them as reliable and trustworthy.               ted values, and informative error messages, because these
   T HUCY remains completely agnostic of both the informa-        are fed back into the LLM. Building a tool also requires
tion content and the internal structure of these tables and       domain expertise. For example, a simple tool that fetches
databases. We provide no additional metadata, schema in-          schema information from a PostgreSQL database requires
formation, or prior knowledge to our multi-agent system.          knowledge of relational databases, Postgres internals, and
Instead, we assume that the grounding data sources are en-        query execution. Building a similar tool for MySQL (antirely unknown before deployment. The agents must there-          other database management system), the developer has to
fore operate in an open-ended environment, discovering and
reasoning about available data as they encounter it.                 1
                                                                       More precisely, it is the LLM that makes this decision, though
   This design makes our approach highly flexible as we can       we often use “agent” and “LLM” interchangeably in such contexts
Table 1: Capabilities of different LLM-based systems for fact verification over structured data. Cross-Table and Cross-Database
refer to a system’s ability to verify claims that span multiple tables or databases. Interpretable means that users can understand
the reasoning behind the model’s verdict. Verifiable goes a step further—it allows users to reproduce the verification process
(e.g., providing the exact Python or SQL commands), eliminating any suspicion of hallucinations. Finally, Source-Agnostic
indicates that the system can operate without prior knowledge of its data environment, figuring out everything from scratch.

    Method                             Cross-Table     Cross-Database       Interpretable     Verifiable   Source-Agnostic
    BINDER (Cheng et al. 2023)               ✗                   ✗                ✓               ✗                 ✗
    DATER (Ye et al. 2023)                   ✗                   ✗                ✓               ✗                 ✗
    CoTable (Wang et al. 2024)               ✗                   ✗                ✓               ✗                 ✗
    ReAcTable (Zhang et al. 2024)            ✗                   ✗                ✗               ✗                 ✗
    AutoTQA (Zhu et al. 2024)                ✓                   ✓                ✗               ✗                 ✗
    POS (Nguyen et al. 2025)                 ✗                   ✗                ✓               ✗                 ✗
    T HUCY (ours)                            ✓                   ✓                ✓               ✓                 ✓


start over, since there are differences in the catalog layout,       tools:
the connection logic, etc. Switching to a different agentic            seattle_sql:
framework might require rebuilding all tools from scratch.               kind: postgres-execute-sql # Google
The solution we adopted for T HUCY was to use MCP.                       source: seattle # Postgres DB
                                                                       portland_sql:
MCP The Model Context Protocol (MCP), introduced                         kind: postgres-execute-sql # Google
by Anthropic (2024), standardizes how AI applications con-               source: portland # Postgres DB
nect to different data sources, effectively eliminating the            los_angeles_sql:
need for custom connections for each new AI model and ex-                kind: mysql-execute-sql # Google
ternal system allowing us to direct our energy elsewhere—                source: los_angeles # MySQL DB
away from repetitive boilerplate code. MCP simplifies and              ...
streamlines the tool building process, and has already been
adopted by industry (Mehrotra 2025; Gonzales and Murching 2025; Ganguly 2025; Agarwal et al. 2025).                        Figure 2: A YAML fragment showing the configuration of
                                                                     database tools; schema-related tools are omitted for brevity.
Toolsets We use Google’s MCP Toolbox for
Databases (Buvaraghan and Egan 2025), a framework
that makes it effortless to organize and manage database             we simply subscribe it to west-coast-schema. The retools. It provides built-in primitives—actual implementa-            sulting configuration is shown in Figure 3.
tions of low-level functions like executing SQL—across                  In the same spirit, we might also maintain a
different database systems (e.g., PostgreSQL, MySQL),                washington-state toolset, bundling together the
ready to use without us having to code anything.                     tools for databases from the Seattle area and other cities
   Using these primitives as building blocks, we define              in WA. Within each database, we can import official data
higher-level tools that bind and interact with specific              from various governmental sources, which T HUCY can then
databases. For example, in Figure 2, we create the tools             explore when verifying claims about the state—exactly as
seattle sql and portland sql, both of which use                      in the ongoing investigation of the City Attorney’s claim
Google’s postgres-execute-sql primitive to run                       from Section 1.
SQL queries on the respective Postgres databases seattle                If we later decide to remove access to a database (say, the
and portland. We also define los angeles sql,                        Portland database), we only need to delete the correspondwhich uses the MySQL primitive mysql-execute-sql,                    ing tools in Figure 3—literally commenting out two lines of
to query the los angeles database.                                   code from the configuration. Conversely, if we want to add
   Of course, there can be many such tool definitions for            another city into the mix, we simply append two more tools.
many different databases. Once the tools are defined, we
can group them into flexible collections called toolsets. Each       Agentic System
agent can then simply “subscribe” to the toolsets it needs.          With the data layer now in place, we turn our attention to the
   As a simple example, suppose we want an agent to in-              core of T HUCY: its multi-agent architecture. Connecting to
vestigate crime statistics across cities in the “West Coast”—        databases modularly is only part of the challenge—the real
Seattle, Portland, and Los Angeles. To do that, it needs ac-         difficulty lies in navigating and reasoning over them effeccess to all three databases. All we have to do is bundle             tively. Our system tackles this through a team of three spethe corresponding tools from Figure 2 into a single toolset,         cialized expert-agents: the Data Expert, Schema Expert and
west-coast-sql, and then subscribe the agent to it. It’s             SQL Expert. Each agent has a distinct role, specific instrucjust as easy to give the agent access to schema information:         tions, clear output expectations, and subscribes to one of the
toolsets:                                                           even hundreds of tables, each with dozens of attributes, and
  west-coast-sql:                                                   the table or column names are frequently non-descriptive.
    - seattle_sql                                                   For example even the relatively well organized Crime Data
    - portland_sql                                                  for Seattle (Seattle Police Department 2025a) has opaque
    - los_angeles_sql                                               column names like NIBRS Group AB or Beat.
  west-coast-schema:                                                   This is where the Schema Expert comes into play. Its
    - seattle_schema                                                high-level role is to answer arbitrary schema-related ques-
    - portland_schema                                               tions about the available databases. It is equipped with the
    - los_angeles_schema                                            schema toolset—similar to the Data Expert—which al-
  washington-state-schema:                                          lows it to fetch detailed schema information from the con-
    - seattle_sql                                                   nected databases. Unlike the Data Expert, however, it oper-
    ...                                                             ates without guardrails and is in fact encouraged to dive deep
  washington-state-sql:                                             into the structural details of the schemata. It can investigate
    - seattle_schema                                                nearly any aspect of the databases’ design; from simple col-
    ...                                                             umn names to specific constraints on those columns (e.g.,
                                                                    foreign key relationships, nullability, and more).
    Figure 3: Example YAML configuration of toolsets                   However, misuse of its own tools can quickly clutter the
                                                                    agent’s memory (for example, by the misfortune of querying
                                                                    the schema of a messy corporate database containing sevtwo toolsets described earlier (sql or schema).                     eral hundred-column tables). To try avoid this as much as
                                                                    possible, we require one additional input to the Schema Ex-
   They are coordinated by the Verifier, a higher-level agent
                                                                    pert. Along with the schema question, we must also provide
responsible for driving the verification process and produc-
                                                                    a brief context hint—this is a short, high-level NL cue that
ing the final verdict on claims—along with a transparent re-
                                                                    steers the agent toward relevant databases (Figure 4).
port containing explanatory SQL queries. Importantly, the
three expert-agents are designed as atomic components: they            All in all, the Schema Expert expects 1 a NL schema
never communicate directly with one another; they interact          question along with 2 a context hint, and investigates the reonly with non-AI static tools exposed through their respec-         lated data sources in order to provide a crisp, precise answer
tive toolsets.                                                      in NL. The exact response and format is left to the agent
   In this section, we discuss the rationale behind our design      and depends on the question at hand. For example, a recent
choices, the challenges we encountered, and the unique so-          query was “List all tables related to to crime, police incilutions that made our approach effective.                           dents, offense categories, or year-by-year statistics.” with
                                                                    the context hint of “Seattle, WA”. The resulting answer was
Data Expert Since the data environment is unknown, with             a well-structured, markdown-formatted summary detailing
potentially many databases and tables, we need a mechanism          the relevant tables, column names, and types.
to rapidly survey the available landscape. This is the role of         During execution, the Verifier frequently invokes the
the Data Expert, which “subscribes” to the schema toolset.          Schema Expert to answer different things about some
Its task is to perform a high-level scan of all accessible data     database’s schema (as in the example above). The responses
sources and summarize what each source appears to contain.          are always clear, complete, and to the point—exactly what
   The usefulness of this step might not be immediately             we want. This design “protects” the Verifier’s expensive conapparent, but it is crucial: data exploration involves nu-          text by allowing it to access highly curated schema informamerous tool calls and exposure to large amounts of low-             tion without having to endure the messiness of retrieving it.
level information—database, table, and column names; data
types, schemas, and various metadata—that must be in-               SQL Expert Once a reasonable understanding of the
evitably consumed to truly understand what the data is              database’s schema has been established, the next step is to
about. The Data Expert’s job is to “bite the bullet” navi-          interact and play around with the data itself. For relational
gating this chaos, and deliver a clean single-paragraph sum-        databases, this means writing SQL. The NL to SQL probmary to the Verifier. This summary enables the Verifier             lem consists of automatically converting a natural language
to plan an effective verification strategy knowing the data         question over a relational database (with known schema) to
sources it has in its disposal, while keeping its expensive         an SQL query (Li and Jagadish 2014; Sen et al. 2020). Decontext from being cluttered by useless details.                    spite lots of progress in this space and the availability of pop-
                                                                    ular benchmarks—like Spider (Yu et al. 2018), KaggleDSchema Expert In order to write any successful query                BQA (Lee, Polozov, and Richardson 2021) and BIRD (Li
over relational databases, the first step is always to under-       et al. 2023)—NL2SQL remains a challenging problem for
stand the schema. In theory, relational databases should have       real-world scenarios, because of schema complexity, query
table and column names that are unambiguous, column types           ambiguity, and semantic mismatch (Floratou et al. 2024).
should match their intended semantics (e.g., an age column             For example, suppose that we want to ask: Which neighis a number and not text), and keys and foreign keys should         borhood of Seattle recorded the most parking tickets in
be explicitly declared in the schema. In practice, this is rarely   the second quarter of 2025? Everyone roughly understands
the case. Corporate or institutional databases have dozens or       what this question means, yet translating it into SQL quickly
                            Data Expert                               The SQL Expert expects two inputs: 1 the NL query it-
                                                                   self, and 2 the relevant database schema information (Fig-
                                               Data
                                             Summary
                                                                   ure 4). The latter contains all the necessary schema details
                                                                   the agent might need to write SQL queries within the scope
                          Schema Expert                            of the question—such as the explicit names of the relevant
             Query                                                 databases, tables, relationships, and columns. This way, the
                                              Answer
         Context Hint                                              agent can focus precisely on the relevant parts of the data,
                            SQL Expert                             without being distracted by the rest of the environment.
             Query                                                 There might be countless other tables or databases avail-
                                              Answer               able, but we want our SQL Expert to enter a kind of “tunnel-
         Schema Info
                                                                   vision” mode, concentrating solely on the question at hand
                                                                   and on the small relevant portion of the data landscape that
Figure 4: Inputs and outputs of the three expert-agents. The       contains the answer.
Data Expert is invoked without input and returns a concise
high-level report of what the connected databases appear to
contain. The Schema Expert expects a schema-related ques-          Verifier Finally, the role of the Verifier is to coordinate
tion along with a short hint about where to look (for exam-        all other agents, and verify the factual claim requested by
ple, “NYC database”), and returns a precise answer to that         the users. The Verifier produces two outputs: a verificaquestion. Lastly, the SQL Expert expects a question about          tion verdict (one of Verified, Partly Verified, Partly Inaccuthe data along with specific information of the schema that        rate, or Inaccurate), and an analytical report containing the
is relevant to the question. The process usually involves a        SQL queries that explain and support this verdict. This recouple of SQL queries on the databases, depending on what          port is organized in a clear, chronological way, effectively
the agent decides. At some point, it returns a clear answer        walking the user through each stage of the verification protogether with the concrete SQL commands that verify it.            cess. If desired, the data analyst can execute the explanation
                                                                   SQL queries herself, examine their outputs, modify and re-
                                                                   execute them, until she is completely satisfied with the vereveals several challenges. First, to compute total parking        racity and generality of the claim.
tickets, we must discover the semantics of “quarter” —is it           To achieve this task, the Verifier interacts with all other
relative to the calendar year or the fiscal year? Sometimes,       agents in the system. In order to ask the SQL Expert somethe best we can do is to infer it by exploring the data itself.    thing about the data, it will provide it with the relevant
For example, by investigating the actual data, we might find       schema information indicating where exactly to look (Figout that the table conveniently includes concatenated infor-       ure 4), obtained from the Schema Expert, while the latter
mation that indicate the quarter (e.g., “Q1” to “Q4”). Even        requires information from Data Expert.
if we are not that lucky, this process still helps us understand
how dates are stored and organized. In other words, while             To summarize, the Verifier begins by asking the Data Exthe question is inherently ambiguous, careful inspection of        pert to provide an overview of the available data sources. Usthe data often reveals its intended meaning. The first stage       ing this information, the Verifier consults the Schema Expert
of query formulation consists of an interactive exploration        to obtain the schema of the relevant databases, initially at
of the data.                                                       some high level of detail (for example, only the table names
   After this exploratory stage, the next stage is to write the    without their attributes). Next, it invokes the SQL Expert to
query or queries that answer the question. Unfortunately,          ask a question about a specific step of the claim verificamany things can still go wrong at this point. We might write       tion, and obtains concrete, verifiable answers consisting of
a logically incorrect query (a semantic mismatch) and only         both SQL queries and their results. Usually, more informarealize it when no results appear—perhaps because we ac-           tion is needed, and the Verifier repeats this in a cycle: ask the
cidentally filtered everything out. On top of that, there are      Schema Expert for more detail, in order to ask the SQL Exthe usual syntax errors, some of which are due to the dif-         pert new queries; if the answers remain unsatisfactory, the
ferent vendor-specific versions of SQL (e.g., PostgreSQL,          Verifier may decide to ask the Data Expert for additional
MySQL, Oracle, etc.) of the available databases.                   relevant data sources, and the process continues. Eventually,
   In summary, NL2SQL is not a one-shot process, but               the Verifier is satisfied and writes the answer to the user.
requires a continuous back-and-forth with the database                Importantly, the Verifier never interacts directly with the
through SQL queries. In T HUCY this is the role of the SQL         messy data sources—it leaves the “dirty work” to the three
Expert. This expert emulates the interactive process in order      experts. They are the ones who dive into the details, explore
to answer questions over the available relational databases.       the data with whatever trials and tribulations, and handle its
To ensure transparency, we instruct it to always also return       inevitable quirks. The Verifier simply asks the right questhe concrete evidence that supports its answer. We want ev-        tions and receives informative, concise, and crisp answers
ery result to be fully traceable back to the data through con-     in return; without ever touching the chaos underneath. Thus,
crete SQL. We instruct the SQL Expert to exclude from the          its context remains light, focused, and packed only with the
answer SQL queries that are irrelevant to the final answer         most useful information. This efficiency allows us to equip
(e.g., exploratory or failed queries).                             the Verifier with a powerful model.
Orchestration                                                            SELECT
In practice, our three expert-agents are wrapped as callable              EXTRACT(YEAR FROM offense_date)::int
functions and exposed to the Verifier as tools. This allows               AS year,
the Verifier to invoke any of them directly, much like calling            offense_category,
a non-AI tool like a calculator. The architecture follows an              COUNT(*) AS incident_count
“Agents as Tools” pattern, where specialized agents are en-              FROM public.crime_data
                                                                         WHERE offense_category IN
capsulated as a tools with clearly defined inputs and outputs.
                                                                             ('PROPERTY CRIME','VIOLENT CRIME')
   For the expert-agents, we persist memory only within a                 AND offense_date >= '2023-01-01'::date
single tool invocation, not across different calls. This design           AND offense_date < '2025-01-01'::date
choice makes the agents reusable atomic components—any                   GROUP BY 1, 2
lead agent, such as the Verifier, can seamlessly employ them             ORDER BY 1, 2;
without inheriting messy context from previous runs. This
keeps the multi-agent system simple, modular, and easy to
                                                                                     Year         Category         Incidents
extend.
                                                                                     2023     Property Crime        40,951
                  3    Verification Example                                          2023     Violent Crime         5,435
                                                                                     2024     Property Crime        41,220
Now, we can turn our focus to the verification example in-                           2024     Violent Crime         5,477
troduced in Section 1. As a reminder, Ann Davison, Seattle’s
City Attorney, made the following statement in the 2024 An-
                                                                         Figure 5: SQL query and results produced by T HUCY
nual Report:
                                                                         when verifying the City Attorney’s claim. The query groups
   I am pleased to acknowledge that 2024 saw a reduc-                    crimes by year and category and counts total incidents.
   tion in property crime and violent crime in Seattle.
   We set out to verify this claim using T HUCY. We have                                      4    Experiments
access to a PostgreSQL database with the City of Seattle’s
official crime data. We had downloaded this data from the                In this section, we present the experimental evaluation of
Seattle Police Department (2025b) in the form of a CSV                   T HUCY. We first describe the widely used fact verification
file, then uploaded it into PostgreSQL. It contains roughly              benchmark TabFact, followed by the baselines. Next, we
1.5M rows of all recorded crimes from 2008 to the present.               outline the framework in which T HUCY was built and the
To verify claims like that by the city’s attorney, we invoked            LLMs it uses. Finally, we present our findings, which show
T HUCY with the verbatim claim above. After a few minutes,               that T HUCY decidedly surpasses the state of the art.
our multi-agent system produces the following report and                 Benchmark We conduct experiments on TabFact (Chen
verdict (excerpted verbatim):                                            et al. 2020), a widely used benchmark for fact verification
   Findings:                                                             over Wikipedia tables. The task is to determine whether a
    – Property crime increased from 40,951 (2023) to                     claim holds given the evidence in a relational table. The
      41,220 (2024), a rise of 269 incidents (∼ 0.7%).                   claim is labeled “false” if any part of it conflicts with the data
    – Violent crime increased from 5,435 (2023) to 5,477                 from the table. Many cases involve subtle linguistic reason-
      (2024), a rise of 42 incidents (∼ 0.8%).                           ing and common sense. Following all prior work (Nguyen
   Conclusion: The claim is contradicted by the data: both               et al. 2025; Zhu et al. 2024; Zhang et al. 2024), we evaluate
   property crime and violent crime were slightly higher in              on the small test split of TabFact, which contains roughly 2k
   2024 than in 2023 in the Seattle dataset examined.                    fact-table pairs.
   Verdict: Inaccurate                                                   Baselines We compare against recent fact-verification sys-
   An important feature of T HUCY is that it also returns the            tems that all rely on LLMs, as these have achieved stateexplanatory SQL query (or queries) that lead it to its verdict.          of-the-art performance (Zhu et al. 2024). We do not reThese queries can be directly inspected, executed, and repro-            implement the baselines; instead, we report the results produced by expert users. In our example, T HUCY generated                  vided in their original papers for the same task and dataset.
the query shown in Figure 5. In essence, the query groups                   We compare against BINDER (Cheng et al. 2023),
crimes by year and category, and then counts the number of               DATER (Ye et al. 2023), CoTable (Wang et al. 2024),
incidents—exactly what we would expect for this verifica-                ReActTable (Zhang et al. 2024), AutoTQA (Zhu et al. 2024),
tion. The output of the query is also shown in the figure. It            and POS (Nguyen et al. 2025).
was easy to run this query ourselves and confirm the cor-                   Among them, AutoTQA is particularly relevant, as it also
rectness of T HUCY’s verdict; we show the answers in the                 builds a multi-agent system and is the only one in the literafigure. We also checked these results on the interactive crime           ture to also support cross-table querying. Their agents follow
dashboard of the City of Seattle (Seattle Police Department              a cyclic orchestration pattern—executing, critiquing, and re2025a), and got the same results.2                                       fining plans in a loop. Our approach differs in two main
                                                                         ways: 1 T HUCY is agnostic to the underlying data environ-
   2
       In the dashboard, make sure that “all” is selected in Precinct.   ment, and 2 it provides concrete traceable evidence along-
side the answers. We also take a different stance on agent          Table 2: Accuracy (↑) on the small test set of the TabFact
orchestration: instead of cyclic pattern, we employ decou-          Benchmark. Some papers decided to re-run the same experipled, specialized expert-agents. This choice is validated by        ments of previous methods using newer models, so we report
recent successful applications in industry (Anthropic 2025).        the new results as well. Each entry points to its source paper.
   POS is also related to our work, as it focuses on interpretability. It returns the execution plan to the user as a logi-    Method                                       Model         Acc (↑)
cal sequence of NL atomic steps. We differ in two key ways:          BINDER (Cheng et al. 2023)                   Codex         85.1%
 1 we output concrete SQL queries, eliminating any suspi-            BINDER (Nguyen et al. 2025)               GPT-4o-mini      84.6%
cion of hallucinations, since expert users can directly verify       DATER (Ye et al. 2023)                       Codex         85.6%
them; and 2 we are not constrained to an answer coming               DATER (Nguyen et al. 2025)                GPT-4o-mini      81.0%
from a single query. In contrast to POS, which assumes the           CoTable (Wang et al. 2024)                  PaLM 2         86.6%
final answer is produced by a single SQL query, we allow—            CoTable (Nguyen et al. 2025)              GPT-4o-mini      84.2%
and in fact encourage—multi-step reasoning where poten-              ReAcTable (Zhu et al. 2024)                  GPT-4         83.4%
tially many arbitrary queries contribute to the final answer         ReAcTable (Zhu et al. 2024)               GPT-4-turbo      85.0%
in different ways.                                                   ReAcTable (Zhang et al. 2024)                Codex         86.1%
Setup We built T HUCY using the OpenAI Agents SDK.                   AutoTQA (Zhu et al. 2024)                    GPT-4         87.4%
Following our discussion in Section 2, we equip the Verifier         AutoTQA (Zhu et al. 2024)                 GPT-4-turbo      88.7%
with a highly capable model (GPT-5), since its context               POS (Nguyen et al. 2025)                  GPT-4o-mini      82.7%
remains lightweight. We then experiment with the expert              T HUCY (ours)                             GPT-4o-mini      93.7%
agents—Data Expert, Schema Expert, and SQL Expert—                   T HUCY (ours)                             GPT-5-mini       94.3%
using two model variants: GPT-5-mini and GPT-4o-mini.
Results As we can see in Table 2, T HUCY beats the previous state of the art by 5.6 percentage points, setting a new      depending on who you ask. After a few minutes, T HUCY
best-known result on TabFact at 94.3%. To test the robust-          returned the following report (excerpted verbatim):
ness of T HUCY, we also swapped the models of our three               Conclusion
expert agents for GPT-4o-mini, aligning them to those used             – The Seattle crime data do not support the claim that
in the baseline systems (e.g., we match POS). The outcome                “violent crime incidents in downtown Seattle dropped
remains the same: T HUCY outperforms the previous state                  by 36%” in Summer (Jun–Aug) 2025 versus the same
of the art by 5 points in accuracy. This result is especially            period in 2024. Depending on how “downtown” is deencouraging—it shows that T HUCY remains effective even                  fined, overall violent crime either increased modestly
when the individual agents use less capable models. It also              or decreased slightly, but nowhere near 36%.
reinforces our design choice of specialized, task-specific
                                                                      Verdict: Inaccurate
agents, since we can confidently downgrade their models to
                                                                       Assumptions and notes
reduce cost without sacrificing much. We believe this de-
                                                                       – “Downtown Seattle” was operationalized as the
composition of the overall task into smaller, well-defined
                                                                         neighborhoods BELLTOWN, DOWNTOWN COMsubtasks, each handled by a dedicated expert agent under a
                                                                         MERCIAL, and PIONEER SQUARE, and also tested
single lead agent, plays a central role in these improvements.
                                                                         with CHINATOWN/INTERNATIONAL DISTRICT in-
                                                                         cluded.
                5    A Journalistic Tale
                                                                    What T HUCY considered as “Downtown Seattle” is, in
A very recent article by MyNorthwest (2025) claimed that            principle, reasonable. Still, before accepting the verviolent crime in downtown Seattle had “plummeted” during            dict, we wanted to dig deeper. The dataset includes a
the summer months compared to the same period last year.            neighborhood attribute, which T HUCY correctly3 leverThe second sentence of the article reads:                           aged to filter by the relevant neighborhoods. This is exactly
   Between June and August 2025, officials reported that            what a data analyst would do too. But this raised an inter-
   violent crime incidents in downtown Seattle dropped              esting question: could there exist some other combination
   by 36% compared to the same period in 2024.                      of neighborhoods—perhaps the one implicitly used by the
                                                                    news articles—for which the 36% drop actually holds?
Within just a few hours, other outlets—including Kiro7                 We dug deeper into the SQL queries produced by T HUCY.
(2025) and Yahoo News (2025)—had picked up and repub-               As experienced SQL users, we tweaked those queries to delished the same story, all citing the original source.              fine “downtown” geographically instead: based on the dis-
   Naturally, having built T HUCY and with the crime dataset        tance from Seattle Central Library (which is undoubtedly
from the Seattle Police Department (2025b) already in hand,         downtown). To our surprise, when we restricted to crimes
we were eager to see what it would say. We submitted the            only within a radius of about 0.7km, the trend of the claim
exact claim verbatim and waited a few minutes for the an-           begun to emerge (Table 3). That only made us more deterswer. Unlike the earlier statement by Seattle’s City Attor-         mined to get to the bottom of this.
ney (Sections 1 and 3), however, this one was trickier. The
                                                                       3
term, “downtown”, in particular, can mean different things                 Or rather incorrectly, as we will see in Section 6
Table 3: Cumulative violent crime counts and percentage             also returns the concrete SQL, we were able to spot this imreduction (Jun–Aug 2024 vs. Jun–Aug 2025). Distance is              mediately.
counted from Seattle’s Downtown Library using latitude and          Assumptions & Ambiguity. Another direction we want to
longitude coordinates available in the data.                        explore is controlling how much the agents rely on assump-
                                                                    tions. Assumptions are useful as this is the only way to com-
          Distance      2024    2025     Reduction                  bat ambiguity in both the data and user questions. However,
          < 0.5km        30       37      −23.33%                   they can also introduce subtle errors (for example, using the
          < 0.7km       112       87       22.32                    wrong current date). We want to experiment with ways to
          < 1.0km       178      146       17.98                    make these assumptions better grounded. One idea is to cre-
          < 1.5km       302      289        4.30                    ate another specialized expert-agent that searches the web.
                                                                    Quantitative Evaluation. In the evaluation of T HUCY, we
                                                                    used TabFact (Chen et al. 2020). There is, however, a mis-
                                                                    match: we propose a system that can navigate data environ-
   After further investigation on the Web, we finally uncov-
                                                                    ments with many databases and tables, while our evaluation
ered the source of the confusion. The original news source
                                                                    is conducted on a single-table benchmark. This is indeed
came from a different article, published by the Downtown
                                                                    the case, but to the best of our knowledge there is no factSeattle Association (2025), which stated:
                                                                    verification benchmark in the literature that focuses on large-
  Violent crime incidents in Seattle police’s M sectors (the        scale cross-table or cross-database data. We believe this is an
  downtown core) declined 36% between June–August                   important next step for fact-verification, and we are actively
  2025 compared to the same period in 2024.                         working on creating one.
This claim is far more specific: it reveals that the 36% refers     Ablation Studies. As we were building T HUCY, we manuspecifically to the police’s M sectors. Admittedly, we were         ally tested and refined each agent, observing both their indinot familiar with this terminology. So, once again, we in-          vidual behavior and their interactions within the full system.
voked T HUCY with the exact wording of this claim. This             However, in this work we do not present systematic ablation
time, it returned the following report:                             studies. A careful evaluation and a systematic study of the
                                                                    contribution of each component—both in isolation and by
   Summary conclusion
                                                                    removing individual agents from the system—is warranted.
   – Using report datetime (report month), violent
     crime incidents in Seattle Police’s sector M (down-            Stateless Expert-Agents. Each expert agent does not pre-
     town) fell from 105 in June–August 2024 to 67                  serve memory across tasks. This is a deliberate design
     in June–August 2025: a −36.19% change, which                   choice, as it allows T HUCY to operate in dynamic data en-
     rounds to −36%. This matches the claim.                        vironments. However, this increases cost, since agents must
                                                                    re-discover information across tasks.
   Verdict: Verified
                                                                    Expensive. Lastly, multi-agent systems like T HUCY burn
With the extra M sector information at hand, T HUCY was             through tokens fast (Anthropic 2025). In our case, factable to verify it. We noticed that this time T HUCY took a dif-     checking all 4K examples in our experiments cost about
ferent route: it filtered the data using attributes like sector.    $183.9 in total. That comes out to roughly 5¢ per example.
We also verified T HUCY ’s findings by cross-checking the           In messy real-world fact-checking scenarios like the one disresults on the interactive crime dashboard of the Seattle Po-       cussed earlier (Section 5), the cost rises to 20¢ per verificalice Department (2025a). The numbers match perfectly.4              tion. Still, we believe that our journalistic use case is high-
   Even though we are not journalists, this whole process           stakes enough that this trade-off is worthwhile. After all, we
convinced us even further of the urgent need for journalis-         can easily imagine journalists at the New York Times being
tic tools that actually produce the concrete SQL evidence           more than happy to spend a few dollars to have their articles
of their verdict. T HUCY is one of them. It doesn’t just give       stamped by T HUCY as verified and fault-proof.
a verdict—the story doesn’t just end there. It can be transformed, magnified, and turned to something greater. This is                              7    Conclusion
what Cohen et al. (2011) envisioned long ago in their pioneering seminal work on computational journalism.                   We described our preliminary results for T HUCY, the first
                                                                    multi-agent claim-verification system that operates over
                                                                    multiple relational databases and provides the concrete SQL
          6    Limitations & Future Work                            evidence behind its verdicts. T HUCY remains agnostic to
Dirty Data. Coming back to the previous example,                    the data environment prior to deployment and must therewhen we first gave T HUCY the ambiguous claim about                 fore figure everything out from scratch. Our experimental redowntown Seattle, it made some assumptions about the                sults on a widely used fact-verification benchmark highlight
neighborhood. It then filtered this attribute with the val-         the strength of our multi-agent design. T HUCY improves the
ues it considered as downtown. So far so good—but what              current state of the art in claim verification.
T HUCY missed was that this column has many missing values. In fact, roughly 50% of them are missing. Since T HUCY                         8    Acknowledgments
   4                                                                We thank the reviewers. This work was supported by NSF
    When reproducing the results, after choosing the year and offense category, keep only beats M1–M3 selected; this is sector M.   III 2507117, NSF SHF 2312195, and NSF IIS 2314527.
                        References                                  Already Serve as A Database Interface? A BIg Bench for
Agarwal, A.; Yarnall, T.; Mauser, A.; Pimpalkhute, H.;              Large-Scale Database Grounded Text-to-SQLs. In Oh, A.;
Reini, J.; and Roy, R. 2025. Introducing Snowflake Man-             Naumann, T.; Globerson, A.; Saenko, K.; Hardt, M.; and
aged MCP Servers for Secure, Governed Data Agents.                  Levine, S., eds., Advances in Neural Information Process-
                                                                    ing Systems 36: Annual Conference on Neural Information
Anthropic. 2024. Introducing the Model Context Protocol.
                                                                    Processing Systems 2023, NeurIPS 2023, New Orleans, LA,
Anthropic. 2025. How we built our multi-agent research              USA, December 10 - 16, 2023.
system.
                                                                    Mehrotra, P. 2025. PayPal Begins Rollout of MCP Servers
Buvaraghan, H.; and Egan, D. 2025. MCP Toolbox for                  to Accelerate Agentic Commerce.
Databases: Simplify AI Agent Access to Enterprise Data.
                                                                    MyNorthwest. 2025. Violent crime plummets 36% in downChen, W.; Wang, H.; Chen, J.; Zhang, Y.; Wang, H.; Li, S.;
                                                                    town Seattle, lowest since 2017.
Zhou, X.; and Wang, W. Y. 2020. TabFact: A Large-scale
Dataset for Table-based Fact Verification. In 8th Interna-          Nguyen, G.; Brugere, I.; Sharma, S.; Kariyappa, S.; Nguyen,
tional Conference on Learning Representations, ICLR 2020,           A. T.; and Lécué, F. 2025. Interpretable LLM-based Table
Addis Ababa, Ethiopia, April 26-30, 2020. OpenReview.net.           Question Answering. Trans. Mach. Learn. Res., 2025.
Cheng, Z.; Xie, T.; Shi, P.; Li, C.; Nadkarni, R.; Hu,              Seattle City Attorney’s Office. 2024. 2024 Annual Report.
Y.; Xiong, C.; Radev, D.; Ostendorf, M.; Zettlemoyer, L.;           Seattle Police Department. 2025a. Seattle Crime Dashboard.
Smith, N. A.; and Yu, T. 2023. Binding Language Models in Symbolic Languages. In The Eleventh International            Seattle Police Department. 2025b. SPD Crime Data: 2008Conference on Learning Representations, ICLR 2023, Ki-              Present.
gali, Rwanda, May 1-5, 2023. OpenReview.net.                        Sen, J.; Lei, C.; Quamar, A.; Özcan, F.; Efthymiou, V.;
Cohen, S.; Li, C.; Yang, J.; and Yu, C. 2011. Computa-              Dalmia, A.; Stager, G.; Mittal, A. R.; Saha, D.; and Sankarational Journalism: A Call to Arms to Database Researchers.          narayanan, K. 2020. ATHENA++: Natural Language QueryIn Fifth Biennial Conference on Innovative Data Systems             ing for Complex Nested SQL Queries. Proc. VLDB Endow.,
Research, CIDR 2011, Asilomar, CA, USA, January 9-12,               13(11): 2747–2759.
2011, Online Proceedings, 148–151. www.cidrdb.org.                  Wang, Z.; Zhang, H.; Li, C.; Eisenschlos, J. M.; Perot, V.;
Downtown Seattle Association. 2025. Economic Revitaliza-            Wang, Z.; Miculicich, L.; Fujii, Y.; Shang, J.; Lee, C.; and
tion - Tracking downtown revitalization.                            Pfister, T. 2024. Chain-of-Table: Evolving Tables in the ReaFloratou, A.; Psallidas, F.; Zhao, F.; Deep, S.; Hagleither,        soning Chain for Table Understanding. In The Twelfth InG.; Tan, W.; Cahoon, J.; Alotaibi, R.; Henkel, J.; Singla,          ternational Conference on Learning Representations, ICLR
A.; Grootel, A. V.; Chow, B.; Deng, K.; Lin, K.; Campos,            2024, Vienna, Austria, May 7-11, 2024. OpenReview.net.
M.; Emani, K. V.; Pandit, V.; Shnayder, V.; Wang, W.; and           Wikipedia. 2025. Thycidides — Wikipedia, The Free EncyCurino, C. 2024. NL2SQL is a solved problem... Not!                 clopedia.
In 14th Conference on Innovative Data Systems Research,             Yahoo News. 2025. Violent crime plummets 36% in downCIDR 2024, Chaminade, HI, USA, January 14-17, 2024.                 town Seattle, lowest since 2017.
www.cidrdb.org.
                                                                    Yao, S.; Zhao, J.; Yu, D.; Du, N.; Shafran, I.; Narasimhan,
Ganguly, R. 2025. Introducing the Azure MCP Server.                 K. R.; and Cao, Y. 2023. ReAct: Synergizing Reasoning
Gonzales, E.; and Murching, S. 2025. Announcing managed             and Acting in Language Models. In The Eleventh InternaMCP servers with Unity Catalog and Mosaic AI Integration.           tional Conference on Learning Representations, ICLR 2023,
Kiro7. 2025. Violent crime plummets 36% in downtown                 Kigali, Rwanda, May 1-5, 2023. OpenReview.net.
Seattle, lowest since 2017.                                         Ye, Y.; Hui, B.; Yang, M.; Li, B.; Huang, F.; and Li, Y.
Lee, C.; Polozov, O.; and Richardson, M. 2021. KaggleD-             2023. Large Language Models are Versatile Decomposers:
BQA: Realistic Evaluation of Text-to-SQL Parsers. In Zong,          Decomposing Evidence and Questions for Table-based ReaC.; Xia, F.; Li, W.; and Navigli, R., eds., Proceedings of          soning. In Chen, H.; Duh, W. E.; Huang, H.; Kato, M. P.;
the 59th Annual Meeting of the Association for Computa-             Mothe, J.; and Poblete, B., eds., Proceedings of the 46th Intional Linguistics and the 11th International Joint Confer-         ternational ACM SIGIR Conference on Research and Develence on Natural Language Processing, ACL/IJCNLP 2021,               opment in Information Retrieval, SIGIR 2023, Taipei, Tai-
(Volume 1: Long Papers), Virtual Event, August 1-6, 2021,           wan, July 23-27, 2023, 174–184. ACM.
2261–2273. Association for Computational Linguistics.               Yu, T.; Zhang, R.; Yang, K.; Yasunaga, M.; Wang, D.; Li,
Li, F.; and Jagadish, H. V. 2014. NaLIR: an interactive nat-        Z.; Ma, J.; Li, I.; Yao, Q.; Roman, S.; Zhang, Z.; and Radev,
ural language interface for querying relational databases. In       D. R. 2018. Spider: A Large-Scale Human-Labeled Dataset
Dyreson, C. E.; Li, F.; and Özsu, M. T., eds., International       for Complex and Cross-Domain Semantic Parsing and TextConference on Management of Data, SIGMOD 2014, Snow-                to-SQL Task. In Riloff, E.; Chiang, D.; Hockenmaier, J.;
bird, UT, USA, June 22-27, 2014, 709–712. ACM.                      and Tsujii, J., eds., Proceedings of the 2018 Conference on
Li, J.; Hui, B.; Qu, G.; Yang, J.; Li, B.; Li, B.; Wang, B.; Qin,   Empirical Methods in Natural Language Processing, BrusB.; Geng, R.; Huo, N.; Zhou, X.; Ma, C.; Li, G.; Chang,             sels, Belgium, October 31 - November 4, 2018, 3911–3921.
K. C.; Huang, F.; Cheng, R.; and Li, Y. 2023. Can LLM               Association for Computational Linguistics.
Zhang, Y.; Henkel, J.; Floratou, A.; Cahoon, J.; Deep, S.;
and Patel, J. M. 2024. ReAcTable: Enhancing ReAct for Table Question Answering. Proc. VLDB Endow., 17(8): 1981–
1994.
Zhu, J.; Cai, P.; Xu, K.; Li, L.; Sun, Y.; Zhou, S.; Su,
H.; Tang, L.; and Liu, Q. 2024. AutoTQA: Towards
Autonomous Tabular Question Answering through MultiAgent Large Language Models. Proc. VLDB Endow.,
17(12): 3920–3933.
