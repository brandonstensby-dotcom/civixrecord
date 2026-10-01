# PROJECT ARCHITECTURE SPECIFICATION
# Project: CivixRecord-OS
# License: MIT License (Free & Open Source)
# Target: Municipal & Civic Public Hearing Automation

---

## 1. System Philosophy & Design Principles
CivixRecord-OS is a public-interest software system designed to foster open governance and complete public transparency. It is engineered to operate without ongoing subscription fees, proprietary vendor lock-in, or closed third-party cloud dependencies.

### Core Principles:
1. **100% Fact-Driven Automation:** All statements, motions, and procedural steps are parsed directly from primary audiovisual records. No editorializing or subjective commentary.
2. **Neutral Verification:** Council actions and statements are cross-referenced strictly against primary-source statutory authorities:
   - Municipal Procedure Bylaws (quorum rules, voting thresholds, speaking time limits).
   - Governing Local Government Acts (statutory requirements for public notice, open meetings, and pecuniary interest disclosure).
3. **Transparent Execution:** Any capture bot operating under this framework MUST announce itself in public meeting text channels upon connection. Secret or surreptitious recording is prohibited by architectural design.
4. **Mandatory Executive Session Fence:** The architecture enforces an automated pause/disconnect gate when council enters closed sessions (in-camera) to protect lawful statutory privacy boundaries.

---

## 2. Decision Tree & Flowchart Synthesis Engine

When a public hearing or council meeting progresses, oral discussions often obscure the actual statutory trajectory of policy decisions. CivixRecord-OS converts transcripts into deterministic procedural flowcharts using standard Mermaid notation.

### Automated Decision Tree Pipeline:
1. **Motion Detection:** Identifies formal language (`"I move that...", "Moved by Councillor X"`).
2. **Procedural Classification:** Categorizes the motion (Main Motion, Amendment, Tabling Motion, Procedural Point of Order).
3. **Debate Mapping:** Logs arguments for and against the motion, citing speakers.
4. **Vote Recording:** Parses roll-call votes, recorded division, or unanimous consents.
5. **Action vs. Stated Intent:** Compares whether a councillor's public remarks in debate match their final recorded vote.
6. **Diagram Output:** Compiles an interactive, embeddable Mermaid.js flowchart summarizing the entire meeting agenda.

---

## 3. Deployment & Review Standards for External AI Evaluators
This project follows strict engineering and code review conventions:
- **Zero Hallucination Tolerance:** Extracted motions and quotes must carry exact monotonic timestamps matching the source video.
- **Hermetic Testing:** All unit and integration tests run offline without active network calls.
- **Clean Modularity:** Ingestion, transcription, procedural analysis, and public publishing are decoupled into distinct subpackages.
