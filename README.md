# CivixRecord-OS: Municipal Meeting Transparency & Decision Verification Engine

CivixRecord-OS is a free, open-source, vendor-neutral platform designed to automate the recording, transcription, procedural analysis, and public archiving of municipal council meetings and public hearings.

The system verifies spoken proceedings against published municipal bylaws and statutory rules of procedure, automatically generates procedural decision flowcharts, tracks policy commitments against executive actions, and publishes verifiable public records.

---

## Key Features

1. **Automated Web Conference Ingestion:**
   - Headless browser client joins public web meeting streams (standard WebRTC / browser interfaces).
   - Zero proprietary SDK dependencies or binary reverse-engineering.
   - Transparent public announcement upon joining (`"Public meeting recording active for archival transparency"`).
   - Automatic termination / pause upon motion to enter closed (*In-Camera*) executive session.

2. **Offline Neural Speech-to-Text:**
   - High-performance local transcription using Faster-Whisper.
   - Timestamped speaker diarization and utterance segment tracking.
   - 100% offline local processing option ($0.00 cloud operational cost).

3. **Bylaw & Procedural Cross-Referencing:**
   - Ingests municipal procedural bylaws and policies in Markdown/PDF.
   - Compares meeting procedure (quorum, motion voting, notice requirements) against statutory mandates.
   - Detects procedural deviations, unannounced votes, or omitted disclosures.

4. **Visual Decision Flowcharts (Mermaid / SVG):**
   - Automatically parses motions, debates, amendments, and voting outcomes into structured decision trees and Mermaid flowcharts.
   - Illustrates which elected official moved, seconded, debated, or opposed specific policy directives.

5. **Action vs. Rhetoric Ledger:**
   - Maintains an empirical matrix comparing statements made during council debate against recorded roll-call votes.
   - Tracks tabled items and long-term administrative follow-up commitments.

6. **Automated Public Video & Transcript Archiving:**
   - Packages audio/video with synchronized captions.
   - Automatically generates timestamped agenda chapter markers.
   - Publishes directly to YouTube (via official YouTube Data API v3) or self-hosted S3/WebDAV mirrors.

---

## Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                            CivixRecord-OS Pipeline                                |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Ingestion Engine ]                                                             |
|    - Headless Chromium meeting capture via Playwright / Virtual Audio Loopback    |
|    - Automatic In-Camera Closed Session detection & stream gating                 |
|                                                                                   |
|  [ Transcription Subsystem ]                                                      |
|    - Local neural STT (Faster-Whisper / ONNX Runtime)                             |
|    - Timestamped segment alignment and speaker assignment                         |
|                                                                                   |
|  [ Procedural Analysis Engine ]                                                   |
|    - Vector / Semantic extraction of Motions, Amendments, and Disclosures         |
|    - Cross-verification against municipal Procedure Bylaw                         |
|    - Decision logic synthesis into Mermaid.js procedural flowcharts               |
|                                                                                   |
|  [ Public Distribution Service ]                                                  |
|    - YouTube Data API v3 publisher with timestamped chapter markers               |
|    - Searchable Markdown/HTML minutes compilation & SHA-256 archive manifest      |
+-----------------------------------------------------------------------------------+
```

---

## Directory Layout

```
civixrecord/
├── __init__.py
├── ingestion/
│   ├── __init__.py
│   ├── web_meeting_client.py    # Headless meeting connector & audio/video sink
│   └── closed_session_gate.py   # In-Camera procedural detection and pause guard
├── transcription/
│   ├── __init__.py
│   └── neural_transcriber.py    # Faster-Whisper offline transcription pipeline
├── analysis/
│   ├── __init__.py
│   ├── motion_extractor.py      # Motion, mover, seconder & vote parser
│   ├── bylaw_verifier.py        # Procedure bylaw rule comparison
│   └── flowchart_generator.py   # Mermaid.js procedural decision tree builder
├── publisher/
│   ├── __init__.py
│   ├── youtube_uploader.py      # YouTube Data API v3 automated publisher
│   └── minutes_compiler.py      # Markdown minutes & transcript generator
└── tests/
    ├── __init__.py
    ├── test_motion_extractor.py # Hermetic unit tests for motion parsing
    ├── test_bylaw_verifier.py   # Procedural rule verification tests
    └── test_flowchart.py        # Flowchart synthesis tests
```

---

## License

This project is licensed under the permissive **MIT License** — free to use, modify, and distribute for all citizens, municipalities, and open-source contributors.
