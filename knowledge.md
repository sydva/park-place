# Park Place

this is a hackathon project to create a marketplace for overnight parking.
we wanted to build something to help the housing insecure.

let's go with simple neobrutalist design, similar to the monopoly board game. Silly and familiar.

## Authentication

**Clerk.dev Implementation Complete!**
- React frontend with Clerk.dev authentication
- Protected routes using ProtectedRoute component
- SignInButton, UserButton, SignIn/SignUp components
- Environment variable configuration for Clerk publishable key

## Setup Instructions

**Backend Setup:**
   - Uses `uv` for Python package management (not pip)
   - Python 3.12+ required (configured in pyproject.toml)
   - `uv venv --python 3.12` to create virtual environment
   - `source .venv/bin/activate && uv pip install -r requirements.txt`

 **Frontend Setup:**
   - `cp site/.env.example site/.env` and add keys

## Architecture

- **Frontend:** React with Clerk.dev authentication
- **Backend:** FastAPI with SQLite database
- look at backend/CLAUDE.md for instructions on how to run and test backend
- **Authentication:** Clerk.dev handles all auth flows
- **Protected Routes:** Map, Add Parking Space, Report License Plate

## meta
tasks in todo.md
this will give you a better sense of what we want. much work to be done!

please update this knowledge document and todos as you to keep all human & AI programmers in sync about state of this project.
