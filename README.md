# BookMatch

BookMatch is a Python application for identifying, enriching, and classifying books from user-provided titles, authors, and optional ISBNs.

The current system combines multi-source book retrieval, candidate resolution, human-in-the-loop selection, an OpenAI classification agent, and an independent Gemini review agent.

## Features

- Accepts a book title, optional author, and optional ISBN
- Retrieves book candidates from multiple external book APIs
- Uses Google Books and Open Library as candidate sources
- Handles provider failures, timeouts, HTTP errors, and invalid responses
- Deduplicates candidates at the provider/candidate level
- Scores and ranks candidate relevance using deterministic title-matching rules
- Filters candidates with no title relevance
- Limits the human-facing candidate list to the top 10
- Removes duplicate entries from the human-facing candidate list
- Automatically resolves unambiguous books
- Uses human-in-the-loop selection when multiple distinct books remain
- Uses OpenAI structured output for book classification
- Uses an independent Gemini model as a classification reviewer
- Reviews both the selected book against the original user input and the proposed classification against the available evidence
- Returns `APPROVED` or `NEEDS_REVISION` review decisions
- Provides a command-line interface
- Includes an automated regression test suite

## Architecture

```text
User Input
    |
    v
BookClassificationWorkflow
    |
    v
Candidate Retrieval
    |
    +----------------------+
    |                      |
    v                      v
Google Books         Open Library
    |                      |
    +----------+-----------+
               |
               v
Candidate Combination
               |
               v
Candidate Deduplication
               |
               v
Relevance Filtering
               |
               v
Relevance Ranking
               |
               v
Top 10 Candidates
               |
               v
Display-level Deduplication
               |
               v
Book Identification / Resolution
               |
        +------+------+
        |             |
        v             v
 AUTO_RESOLVE       HITL
        |             |
        |             v
        |       Human Selection
        |             |
        +------+------+
               |
               v
          EnrichedBook
               |
               v
       OpenAI Classifier Agent
               |
               v
       BookClassification
               |
               v
      Gemini Reviewer Agent
               ^
               |
      Original User Input
               |
               v
      ClassificationReview
               |
        +------+------+
        |             |
        v             v
    APPROVED     NEEDS_REVISION
        |
        v
    BookMatchResult
        |
        v
       CLI
```

## Agent Responsibilities

### Classifier Agent

The classifier proposes a structured classification for the selected book.

Current backend:

```text
OpenAI
```

It produces:

- Recommended age group
- Recommended age range
- Reading difficulty
- Primary genre
- Internal classification confidence

### Independent Reviewer Agent

The reviewer independently evaluates the classifier's proposal.

Current backend:

```text
Google Gemini
```

The reviewer receives:

- Original user input
- Selected/enriched book
- Proposed classification

It checks:

- Whether the selected book matches the original user request
- Whether the age group and age range are consistent with the book
- Whether reading difficulty is reasonable
- Whether the primary genre is appropriate

The reviewer returns:

- `approved`
- `needs_revision`
- Review confidence
- Review reason

The classifier and reviewer are intentionally separated behind different interfaces so that the review backend can be replaced independently.

## Candidate Resolution

Candidate retrieval is intentionally separated from identification and resolution.

The candidate pipeline is:

```text
Provider retrieval
    ↓
Combine candidates
    ↓
Deduplicate
    ↓
Remove zero-relevance candidates
    ↓
Rank by title relevance
    ↓
Limit to top 10
    ↓
Display-level deduplication
    ↓
Identification / HITL
```

The relevance scorer uses deterministic rules rather than an LLM. The current scoring policy distinguishes:

```text
Exact title                         100
Exact query phrase                   75
All query tokens, close/same order   50
Distant or partial token overlap     25
No overlap                            0
```

The human-facing candidate list is limited to 10 entries.

Display-level deduplication removes repeated entries with the same normalized title and author while preserving distinct works.

## Human-in-the-Loop

When the system cannot safely distinguish between multiple distinct works, it asks the user to select one candidate.

For example:

```text
Multiple possible books were found:
1. Dog Man — Dav Pilkey
2. Dog Man — Maurice Procter
...

Select a book (1-10):
```

After the user selects a candidate, the selected book continues through the same classification and review stages as an automatically resolved book.

## Project Structure

```text
src/
└── bookmatch/
    ├── batch/
    │
    ├── models/
    │   ├── book.py
    │   ├── book_candidate.py
    │   ├── book_identification.py
    │   ├── book_resolution.py
    │   ├── candidate_evidence.py
    │   ├── classification.py
    │   ├── classification_review.py
    │   └── result.py
    │
    ├── services/
    │   ├── book_candidate_service.py
    │   ├── book_classifier_agent.py
    │   ├── book_identification_service.py
    │   ├── book_information_service.py
    │   ├── book_resolution_service.py
    │   ├── book_resolver.py
    │   ├── book_reviewer_agent.py
    │   ├── candidate_deduplication.py
    │   ├── candidate_display_deduplication.py
    │   ├── candidate_ranking.py
    │   ├── candidate_relevance.py
    │   ├── composite_book_candidate_service.py
    │   ├── gemini_reviewer_agent.py
    │   ├── google_books_book_candidate_service.py
    │   ├── google_books_client.py
    │   ├── open_library_book_candidate_service.py
    │   ├── openai_classification_service.py
    │   ├── openai_reviewer_agent.py
    │   └── exceptions.py
    │
    ├── workflow/
    │   └── book_classification_workflow.py
    │
    └── cli.py

tests/
└── ... comprehensive unit and integration tests ...

data/
└── Briarcliff_Summer_Reading_Master_Book_List_2026.xlsx
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd bookmatch
```

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_openai_api_key
GOOGLE_BOOKS_API_KEY=your_google_books_api_key
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` or API keys to source control.

## Usage

Run:

```bash
uv run bookmatch
```

The application prompts for:

```text
Enter book title:
Enter author (optional):
Enter ISBN (optional):
```

Example:

```text
Enter book title: 16 Forever
Enter author (optional):
Enter ISBN (optional):

Multiple possible books were found:
1. 16 Forever — Lance Rubin
2. 16 Forever — Diana Frances Ferrell
...

Select a book (1-10): 1

---------------------------------------------
BookMatch Result:

Title: 16 Forever
Author: Lance Rubin
Recommended age group: High School
Recommended age range: 14–18 years old
Reading difficulty: 3 / 5
Genre: Young Adult Fiction
---------------------------------------------
Review Details:

Review decision: approved
Review confidence: 0.98
Review reason: ...
```

## Testing

Run the full test suite:

```bash
uv run pytest -q
```

Current checkpoint:

```text
222 passed
```

The test suite covers:

- Book and classification models
- Service and agent interfaces
- Google Books and Open Library behavior
- Provider fallback behavior
- Network failures and timeouts
- HTTP errors
- Candidate combination and deduplication
- Candidate relevance scoring
- Candidate ranking and top-10 limiting
- Display-level candidate deduplication
- Book identification and resolution
- Human-in-the-loop CLI behavior
- Workflow orchestration
- OpenAI structured-output classification
- Gemini structured-output review
- Reviewer approval and revision decisions
- Invalid or missing LLM outputs
- Regression behavior across the complete application

## Technologies

- Python
- uv
- Pydantic
- httpx
- pytest
- OpenAI API
- Google Gemini API
- Google Books API
- Open Library API

## Development History

### Phase 1 — Basic LLM Classification

The initial version established the basic end-to-end workflow:

```text
User Input
    ↓
Book Information Enrichment
    ↓
LLM Classification
    ↓
Classification Result
```

The goal was to build a reliable foundation for external API access, failure handling, and structured LLM output.

### Phase 1.5 — Enhanced Single-Agent Baseline

Phase 1.5 expanded the classifier output to include:

- Recommended age group
- Recommended age range
- Reading difficulty
- Genre

This established a richer single-agent baseline before introducing multiple agents.

### Phase 2A — Candidate Resolution and Human-in-the-Loop

Phase 2A introduced:

- Multi-provider candidate retrieval
- Candidate evidence
- Candidate deduplication
- Book identification
- Book resolution policy
- Automatic resolution for clear matches
- Human-in-the-loop selection for ambiguous matches

The CLI was explicitly kept responsible for user interaction.

### Phase 2B — Classifier and Independent Reviewer Agents

Phase 2B introduced explicit agent interfaces:

```text
BookClassifierAgent
BookReviewerAgent
```

The classifier proposes a classification, while the reviewer independently evaluates it.

The reviewer was deliberately given the original user input in addition to the selected book and proposed classification. This allows the reviewer to detect candidate-selection errors as well as classification errors.

The production configuration uses:

```text
OpenAI → Classifier
Gemini → Reviewer
```

This cross-model design provides an independent second-model perspective instead of asking the same model to validate its own output.

### Phase 2C — Candidate Relevance and Display Quality

Candidate retrieval was further improved with:

- Deterministic title relevance scoring
- Candidate ranking
- Removal of zero-relevance candidates
- Top-10 candidate limiting
- Display-level deduplication

These changes were motivated by real CLI tests in which external search APIs returned large numbers of weakly related or duplicate records.

## Real-World Validation Examples

The current system has been tested interactively with several representative cases.

### Correct candidate

```text
16 Forever — Lance Rubin
→ OpenAI classification
→ Gemini reviewer: APPROVED
```

### Incorrect candidate selected by the human

```text
Dog Man
→ Man and dog — Brad Steiger
→ Gemini reviewer: NEEDS_REVISION
```

### Incorrect author metadata

```text
Dog Man
→ Dog Man — Amanda Gorman
→ Gemini reviewer: NEEDS_REVISION
```

### Teacher's guide selected instead of the requested children's novel

```text
Charlotte's Web
→ Reading, Thinking & Caring Teacher's Guide...
→ Gemini reviewer: NEEDS_REVISION
```

These cases demonstrate that the reviewer can validate both candidate consistency and classification consistency.

## Development Roadmap

```text
Phase 1
Basic LLM Classification
        ↓
Phase 1.5
Enhanced Single-Agent Baseline
        ↓
Phase 2A
Candidate Resolution + Human-in-the-Loop
        ↓
Phase 2B
Classifier Agent + Independent Reviewer Agent
        ↓
Phase 2C
Candidate Relevance + Ranking + Display Control
        ↓
Future
Revision / Reclassification Loop
        ↓
Future
Evaluation Framework
        ↓
Future
Advanced Agent Orchestration
```

The project is currently paused at a stable Phase 2 checkpoint. Future work will be added only where it provides a meaningful improvement over the current architecture and baseline.

## Design Principles

BookMatch is developed incrementally with an emphasis on:

- Clear separation of responsibilities
- Explicit service and agent interfaces
- Structured inputs and outputs
- Deterministic logic where deterministic logic is sufficient
- External-service failure handling and fallback behavior
- Human-in-the-loop handling for genuine ambiguity
- Independent review rather than self-validation
- Test-first development and regression safety
- Reproducible development milestones
- Avoiding unnecessary special-case rules
- Measuring whether additional agentic complexity provides a meaningful benefit

The system deliberately separates retrieval, resolution, classification, and review so that each component can evolve independently.
