# Rahalah - Trip Planning Assistant

A conversational AI-powered trip planning assistant that helps users search for flights and hotels through a natural language interface.

## Features

- **Conversational Trip Search**: Search for flights and hotels using natural language
- **AI-Powered Chat Interface**: Powered by Gemini 2.5 Pro and Rasa for natural language understanding
- **Travel Information**: Retrieve real-time travel data using the Google SERP API (MVP) with future plans for direct API integrations

## Tech Stack

- **Backend**: Python 3.9+ with FastAPI
- **AI/NLP**: Rasa for NLU and Gemini 2.5 Pro for conversation
- **Frontend**: React.js for UI (planned)
- **Database**: PostgreSQL (planned)
- **Deployment**: Docker & AWS (planned)

## Project Structure

```
rahalah/
├── api/            # FastAPI routes and API definitions
├── core/           # Core application logic
├── models/         # Data models and database schemas
├── services/       # External service integrations (Google SERP, etc.)
└── utils/          # Utility functions and helpers
```

## Getting Started

### Prerequisites

- Python 3.9+
- Poetry (dependency management)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   poetry install
   ```
3. Run the development server:
   ```
   poetry run uvicorn rahalah.api.main:app --reload
   ```

## Documentation

- [PRD](prd.md) - Product Requirements Document
- [TODO](todo.md) - Development Plan and Tool List
