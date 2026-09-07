# BookMatch

BookMatch is a Python application that retrieves and enriches book information from external APIs and uses an LLM to classify books by:

- Title
- Author
- Age Group
- Age Range
- Difficulty Level
- Genre

## Features

- Accepts a book title, author, and optional ISBN
- Retrieves book information from external book APIs
- Uses Google Books as the primary information source
- Falls back to Open Library when the primary service fails
- Handles network timeouts, connection errors, HTTP errors, and invalid API responses
- Uses OpenAI structured output for book classification
- Provides a simple command-line interface
- Includes automated tests for core functionality and error handling

## Architecture

```text
User Input
    ↓
BookClassificationWorkflow
    ├── BookInformationService
    │     └── FallbackBookInformationService
    │           ├── Google Books
    │           └── Open Library
    │
    ↓
EnrichedBook
    ↓
OpenAIClassificationService
    ↓
BookClassification
    ├── Age Group
    ├── Age Range
    ├── Difficulty
    └── Genre
    ↓
BookMatchResult
    ├── Book
    └── Classification
    ↓
CLI
```

## Project Structure

```text
src/
└── bookmatch/
    ├── models/
    │   ├── book.py
    │   ├── classification.py
    │   └── result.py
    │
    ├── services/
    │   ├── book_information_service.py
    │   ├── fallback_book_information_service.py
    │   ├── google_books_book_information_service.py
    │   ├── open_library_book_information_service.py
    │   ├── openai_classification_service.py
    │   └── rule_based_classification_service.py
    │
    └── workflow/
        └── book_classification_workflow.py

tests/
├── test_book_information_service.py
├── test_book_classification_workflow.py
├── test_classification.py
├── test_fallback_book_information_service.py
├── test_google_books_book_information_service.py
├── test_open_library_book_information_service.py
├── test_openai_classification_service.py
├── test_result.py
└── test_rule_based_classification_service.py
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd bookmatch
```

Install the project dependencies:

```bash
uv sync
```

Set your OpenAI API key in a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the application:

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
Enter book title: Charlotte's Web
Enter author (optional):
Enter ISBN (optional):

Title: Charlotte's Web
Author: E. B. White
Recommended age group: Middle School
Recommended age range: 11–14 years old
Reading difficulty: 3 / 5
Genre: Fantasy
```

Another example:

```text
Enter book title: Dog Man
Enter author (optional):
Enter ISBN (optional):

Title: Dog Man
Author: Dav Pilkey
Recommended age group: Early Elementary
Recommended age range: 5–7 years old
Reading difficulty: 2 / 5
Genre: Children's Fiction
```

## Testing

Run the full test suite:

```bash
uv run pytest
```

At the Phase 1.5 checkpoint:

```text
32 passed
```

The test suite covers:

- Book information service interfaces
- External API integration behavior
- Fallback behavior
- Network failures and timeouts
- HTTP errors
- Invalid API responses
- Book classification models
- Workflow orchestration
- Rule-based classification
- OpenAI structured output
- Invalid or missing LLM classification results

## Technologies

- Python
- uv
- Pydantic
- httpx
- OpenAI API
- Google Books API
- Open Library API
- pytest

## Phase 1 — Basic LLM Classification

The initial version of BookMatch established the basic end-to-end workflow:

```text
User Input
    ↓
Book Information Enrichment
    ↓
LLM Classification
    ↓
Classification Result
```

The goal of Phase 1 was to establish a reliable foundation for retrieving book information, handling external service failures, and producing structured LLM classification results.

## Phase 1.5 — Enhanced Single-Agent Classification

Phase 1.5 extends the original classifier with a richer structured output.

The system now produces:

- Recommended age group
- Recommended age range
- Reading difficulty
- Genre

The classification is still performed by a **single LLM-based classification service**.

No multi-agent orchestration, agent-to-agent communication, evaluation agent, or review loop is introduced at this stage.

The purpose of Phase 1.5 is to establish a stronger **single-agent baseline** before introducing a multi-agent architecture.

This baseline provides a reference point for evaluating whether a multi-agent system can improve:

- Classification quality
- Reasoning consistency
- Output completeness
- Handling of disagreements
- Reliability of final recommendations

## Development Roadmap

```text
Phase 1
Basic LLM Classification
        ↓
Phase 1.5
Enhanced Single-Agent Baseline
        ↓
Phase 2
Multi-Agent Book Classification
        ↓
Specialized Agents
        ↓
Orchestration
        ↓
Evaluation
        ↓
Review and Revision
```

The next phase will explore a multi-agent architecture in which different agents have specialized responsibilities rather than relying on a single general-purpose classification prompt.

## Design Principles

BookMatch is being developed incrementally with an emphasis on:

- Clear separation of responsibilities
- Structured inputs and outputs
- Explicit service interfaces
- Failure handling and fallback behavior
- Testable components
- Reproducible development milestones
- Measurable evaluation of system improvements

The multi-agent architecture will be introduced only where specialized reasoning, orchestration, evaluation, or review provides a meaningful advantage over the single-agent baseline.
