# Park Place

this is a hackathon project to create a marketplace for overnight parking.
we wanted to build something to help the housing insecure.

let's go with simple neobrutalist design, similar to the monopoly board game. Silly and familiar.

## Authentication

**SuperTokens Implementation Complete!**
- FastAPI backend with SuperTokens Python SDK
- React frontend with SuperTokens React SDK
- Email/password authentication
- Session management with secure HTTP-only cookies
- Protected routes for authenticated users
- Docker Compose setup for local SuperTokens core

## Backend Architecture

- FastAPI with SuperTokens middleware
- In-memory database (for hackathon)
- API routes for parking spaces and user profiles
- CORS configured for React frontend

## Frontend Architecture

- React with SuperTokens auth wrapper
- Protected routes using SessionAuth
- Authentication state management
- Login/signup via SuperTokens pre-built UI

## Development Setup

1. Start SuperTokens: `docker-compose up -d`
2. Start backend: `cd backend && python -m uvicorn main:app --reload`
3. Start frontend: `cd site && npm start`

## meta
tasks in todo.md
this will give you a better sense of what we want. much work to be done!

please update this knowledge document and todos as you to keep all human & AI programmers in sync about state of this project.
