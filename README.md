# AI Plagiarism Web App (Next.js Edition)

## Overview

The AI Plagiarism Web App is a full-stack application designed to detect plagiarism in various forms of content. It features a Next.js frontend and a FastAPI backend. The application utilizes a combination of NLP techniques, image processing, and video analysis to provide an originality score, detailed reports, scan history, and a GPT-powered text humanization tool.

This project demonstrates a comprehensive approach to building AI-powered web applications, incorporating a modern frontend stack, a robust backend with database integration, and various AI-driven features. Some AI components (like reverse image search and audio transcription) use placeholder or mocked logic, highlighting areas for future integration with production-grade services.

## Core Features

*   **Modern Frontend (Next.js 14+)**:
    *   Responsive and interactive UI built with Tailwind CSS.
    *   Smooth page transitions and component animations using Framer Motion.
    *   Dark/Light mode theme toggle provided by `next-themes`.
    *   Client-side routing and state management (React Context) for a seamless user experience.
    *   Modern UI/UX refinements like toast notifications for feedback and client-side form validation.
*   **Comprehensive Plagiarism Checking**:
    *   **📝 Text Checker**: Accepts direct text input or file uploads (.txt, .pdf, .docx). Extracts text and uses a `sentence-transformers` model (`all-MiniLM-L6-v2`) for self-similarity analysis.
    *   **🖼️ Image Checker**: Accepts image uploads (.jpg, .png, .gif). Calculates perceptual image hashes and simulates reverse image search using a *mocked* database.
    *   **🎥 Video Checker**: Accepts video uploads (.mp4). Extracts audio (with *placeholder* transcription) and frames. Performs NLP self-similarity on audio text and mocked reverse search on frame hashes.
*   **📊 Detailed Reports**:
    *   Auto-generated reports display an originality score, specific findings (e.g., similar sentences, matched image sources from mock DB), and actionable rewrite suggestions.
    *   "Export Results" button allows downloading a text summary of the current scan.
*   **👤 User Authentication & Personalized Experience**:
    *   Secure user registration and login system using JWT-based authentication.
*   **Tiered Pricing & Usage Limits**:
    *   A dedicated `/pricing` page displays plan features in both card and table formats.
    *   The backend enforces feature gates and usage limits based on user subscription plans (Free, Pro Basic, etc.). This includes monthly word counts, file size limits, and feature access for history and report downloads.
*   **User-specific scan history dashboard** with Card and Table views to review past checks.
*   Persistent user, history, and usage data stored in a database (SQLite by default).
*   **✨ GPT-Powered Text Humanization**:
    *   An AI tool to rephrase user-provided text using an OpenAI GPT model (defaulting to `gpt-4-turbo`). Usage is metered based on the user's plan. Requires an OpenAI API key.
*   **🤖 FastAPI Backend**:
    *   Serves dedicated endpoints for plagiarism checking, authentication, scan history, AI tools, and a mock admin tool for setting user plans.
    *   Includes a multi-file preview endpoint (`/api/check`) that extracts text from various document types (via byte stream processing) and returns quick previews.
    *   Modular services for text processing (filepath and byte-based), NLP, image analysis, and video processing.
*   **🧪 Testing Setup**:
    *   Backend unit tests for key services and utilities (auth, text processing, history, AI services).
    *   Frontend component testing setup using Jest and React Testing Library, with example tests for key components.

## Technology Stack

*   **Frontend**:
    *   Next.js 14+ (App Router)
    *   React 18+
    *   TypeScript
    *   Tailwind CSS
    *   Framer Motion (for animations and page transitions)
    *   `next-themes` (for dark/light mode theme management)
    *   Heroicons (for UI icons)
    *   Jest & React Testing Library (for component testing)
*   **Backend**:
    *   Python 3.x (project developed with 3.11+)
    *   FastAPI
    *   Uvicorn (ASGI server)
    *   SQLAlchemy (ORM for database interaction)
    *   Alembic (for database migrations)
    *   SQLite (default database, easily configurable for PostgreSQL, etc.)
    *   `sentence-transformers` & `torch` (for NLP text similarity)
    *   `openai` (for GPT model integration)
    *   `Pillow`, `imagehash` (for image processing and hashing)
    *   `opencv-python` (for video frame extraction)
    *   `moviepy` (for audio extraction from video)
    *   `python-jose[cryptography]`, `passlib[bcrypt]` (for JWT authentication)
    *   `pdfminer.six`, `python-docx` (for document text extraction)
    *   `python-dotenv` (for environment variable management)

## Setup and Installation

### Prerequisites

*   Node.js (v18.x or later recommended for Next.js 14)
*   `npm` (or `yarn`/`pnpm`)
*   Python 3.8+ (project developed with 3.11+)
*   `pip` (Python package installer)
*   **OpenAI API Key**: Required *only* for the Text Humanization feature.

### Backend Setup

1.  **Navigate to the project root directory.**
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This installation includes `torch`, which can be large. If you encounter "No space left on device" errors in very constrained environments, ensure adequate disk space.*
4.  **Set up Environment Variables (Backend)**:
    *   Create a `.env` file in the **project root directory**.
    *   **Database URL (Optional)**: Defaults to a SQLite database (`test.db`) in the project root. To use PostgreSQL, set `DATABASE_URL="postgresql://user:pass@host:port/dbname"`.
    *   **OpenAI API Key (Optional)**: Add `OPENAI_API_KEY="your_openai_api_key_here"` to use the Text Humanization feature.
    *   **JWT Secret Key (Recommended)**: Override the default by setting `SECRET_KEY="your_very_strong_random_secret_key_for_jwt"`.
5.  **Apply Database Migrations:**
    *   Navigate to the `backend` directory: `cd backend`
    *   Run Alembic migrations: `alembic upgrade head`
    *   Navigate back to project root: `cd ..`
    *(If `alembic` is not found, try `python -m alembic upgrade head` from the `backend` directory).*
6.  **Run the FastAPI Backend Server:**
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```

### Frontend Setup (Next.js)

1.  **Navigate to the `frontend` directory:** `cd frontend`
2.  **Install Node.js dependencies:** `npm install`
3.  **Set up Environment Variables (Frontend - Optional)**:
    *   If your backend runs on a different URL, create a `.env.local` file in the `frontend` directory with: `NEXT_PUBLIC_API_BASE_URL=http://your_backend_api_url`
4.  **Run the Next.js Development Server:**
    ```bash
    npm run dev
    ```
    The frontend will typically be available at `http://localhost:3000`.

## How to Use

1.  **Ensure both backend and frontend servers are running.**
2.  **Access the Application**: Open `http://localhost:3000`.
3.  **Authentication**: Register for a new account or log in. Login is required to save and view scan history.
4.  **View Pricing**: Navigate to the "Pricing" page from the header to compare plan features.
5.  **Checking Content (Home Page)**: Use the forms to check text, upload documents, images, or videos. Results appear dynamically below.
6.  **Text Humanization (Home Page)**: Use the GPT-powered tool to rephrase text (requires API key).
7.  **Scan History (History Page)**: View past scans in a card or table layout. Click "View Details" for a full report in a modal.
8.  **Multi-File Preview API (For Programmatic Use)**: The `POST /api/check` endpoint can be used by other tools to get quick text previews from multiple files.

## Running Tests

*   **Backend**: Navigate to the `backend` directory and run `python -m unittest discover -s tests`.
*   **Frontend**: Navigate to the `frontend` directory and run `npm test`.
    *   *Note: Frontend test execution may fail in some sandboxed environments due to module resolution issues. The configuration is standard and should work in a local setup.*

## Current Limitations & Mocked Components
(This section remains largely the same, detailing mocked reverse image search, placeholder audio transcription, and focus on self-similarity.)

## Deployment Considerations (Production Environment)
(This section remains largely the same, detailing production-ready practices.)

This README provides a comprehensive guide to understanding, setting up, and using the AI Plagiarism Web App.
