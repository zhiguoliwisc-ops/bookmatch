# BookMatch

BookMatch is a Python application that retrieves and enriches book information from external APIs and uses an LLM to classify books by:

- Recommended age group
- Reading difficulty

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
    │
    ▼
BookClassificationWorkflow
    │
    ├── BookInformationService
    │       │
    │       └── FallbackBookInformationService
    │               ├── GoogleBooksBookInformationService
    │               └── OpenLibraryBookInformationService
    │
    ▼
EnrichedBook
    │
    ▼
OpenAIClassificationService
    │
    ▼
BookClassification
    │
    ├── Recommended age group
    └── Reading difficulty
```

## Project Structure

```text
src/
└── bookmatch/
    ├── models/
    ├── services/
    │   ├── book_information_service.py
    │   ├── fallback_book_information_service.py
    │   ├── google_books_book_information_service.py
    │   ├── open_library_book_information_service.py
    │   ├── openai_classification_service.py
    │   └── rule_based_classification_service.py
    └── workflow/

tests/
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

Example:

```text
Enter book title: Charlotte's Web
Enter author (optional):
Enter ISBN (optional):

Recommended age group: Elementary
Reading difficulty: 3
```

## Testing

Run the test suite:

```bash
uv run pytest
```

Current test status:

```text
28 passed
```

## Technologies

- Python
- uv
- httpx
- OpenAI API
- Google Books API
- Open Library API
- pytest