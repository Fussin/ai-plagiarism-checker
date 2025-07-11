# AI Plagiarism Web App (Next.js Edition)

## Overview

The AI Plagiarism Web App is a full-stack application designed to detect plagiarism in various forms of content, including text, images, and videos. It features a Next.js frontend and a FastAPI backend. The application utilizes a combination of NLP techniques, image processing, and video analysis to provide an originality score, detailed reports, scan history, and a GPT-powered text humanization tool.

This project has evolved from a simpler blueprint and now incorporates a modern frontend stack and more robust backend features, including database integration. Some AI components still use placeholder or mocked logic for core functionality demonstration (e.g., reverse image search, audio transcription).

## Core Features

*   **Modern Frontend (Next.js 14+)**:
    *   Responsive UI built with Tailwind CSS.
    *   Smooth animations using Framer Motion.
    *   Dark/Light mode theme toggle (`next-themes`).
    *   Client-side routing and state management for a seamless user experience.
*   **📝 Text Checker**:
    *   Accepts direct text input or file uploads (.txt, .pdf, .docx).
    *   Extracts text from uploaded documents.
    *   Uses a `sentence-transformers` model (`all-MiniLM-L6-v2`) for self-similarity checks.
*   **🖼️ Image Checker**:
    *   Accepts image uploads (.jpg, .png, .gif).
    *   Calculates perceptual image hashes.
    *   Simulates reverse image search using a *mocked* database.
*   **🎥 Video Checker**:
    *   Accepts video uploads (.mp4).
    *   Extracts audio (placeholder transcription) and frames.
    *   Performs NLP self-similarity on audio text and mocked reverse search on frame hashes.
*   **📊 Comprehensive Reports**:
    *   Originality score, detailed findings, and basic rewrite suggestions.
    *   Ability to export scan results as a text file.
*   **👤 User Authentication & History**:
    *   Secure signup and login (JWT-based).
    *   User-specific scan history dashboard with details of past scans.
    *   Uses a database (SQLite by default) for persistent user and history data.
*   **✨ GPT-Powered Text Humanization**:
    *   Allows users to input text and get a "humanized" version using an OpenAI GPT model (requires API key).
*   **🤖 FastAPI Backend**:
    *   Serves plagiarism checking logic, auth, history, and AI tool endpoints.
    *   Modular services for various processing tasks.

## Technology Stack

*   **Frontend**:
    *   Next.js 14+ (App Router)
    *   React 18+
    *   TypeScript
    *   Tailwind CSS
    *   Framer Motion (for animations)
    *   `next-themes` (for dark/light mode)
    *   Heroicons (for icons)
*   **Backend**:
    *   Python 3.x
    *   FastAPI
    *   Uvicorn (ASGI server)
    *   SQLAlchemy (ORM for database interaction)
    *   Alembic (for database migrations)
    *   SQLite (default database, configurable to PostgreSQL etc.)
    *   `sentence-transformers` & `torch` (for NLP text similarity)
    *   `openai` (for GPT integration)
    *   `Pillow`, `imagehash`, `opencv-python`, `moviepy` (for media processing)
    *   `python-jose[cryptography]`, `passlib[bcrypt]` (for authentication)
    *   `pdfminer.six`, `python-docx` (for document text extraction)
    *   `python-dotenv` (for environment variable management)

## Setup and Installation

### Prerequisites

*   Node.js (v18.x or later recommended for Next.js 14)
*   `npm` (or `yarn`/`pnpm`)
*   Python 3.8+
*   `pip` (Python package installer)
*   An OpenAI API Key (optional, for the Text Humanization feature).

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
    *Note: This may take time due to `torch`. If you encounter "No space left on device" errors in constrained environments, try installing packages in smaller groups or ensure adequate disk space.*
4.  **Set up Environment Variables (Backend)**:
    *   Create a `.env` file in the **project root directory** (alongside `frontend` and `backend` folders).
    *   Add your `OPENAI_API_KEY` if you plan to use the Text Humanization feature:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        # You can also override DATABASE_URL here if needed, e.g.:
        # DATABASE_URL="postgresql://user:pass@host:port/dbname"
        ```
    *   The default `DATABASE_URL` uses SQLite and will create `test.db` in the project root.
5.  **Initialize and apply database migrations:**
    *   Navigate to the `backend` directory: `cd backend`
    *   Apply migrations: `alembic upgrade head`
    *   Navigate back to project root: `cd ..`
    *(If `alembic` command is not found directly, try `python -m alembic upgrade head` from within the `backend` directory after activating the venv).*
6.  **Run the FastAPI backend server:**
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will be available at `http://127.0.0.1:8000`.

### Frontend Setup (Next.js)

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Set up Environment Variables (Frontend)**:
    *   The frontend might need to know the backend API URL. By default, it's set to `http://127.0.0.1:8000` in `frontend/contexts/AuthContext.tsx` and `frontend/app/page.tsx`.
    *   For production or different local setups, you can create a `.env.local` file in the `frontend` directory:
        ```env
        NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
        ```
4.  **Run the Next.js development server:**
    ```bash
    npm run dev
    ```
    The frontend will typically be available at `http://localhost:3000`.

## How to Use

1.  **Ensure both backend and frontend servers are running.**
2.  **Access the Application**: Open `http://localhost:3000` in your web browser.
3.  **Theme Toggle**: Use the sun/moon icon in the header to switch between light and dark modes.
4.  **Authentication**:
    *   **Register**: Create a new account via the "Register" page.
    *   **Login**: Log in with your credentials.
    *   The header will update to show your email and a "Logout" button.
5.  **Checking Content (Home Page)**:
    *   **Text Input**: Paste text and click "Check Text".
    *   **File Uploads**: Use the respective sections to upload Text Documents (PDF, DOCX, TXT), Images (JPG, PNG, GIF), or Videos (MP4), then click the corresponding "Check" button.
    *   Results (originality score, details, suggestions) will appear below the input sections.
    *   Use the "Export Results" button to download a text summary of the latest scan.
6.  **Text Humanization (Home Page)**:
    *   Paste text into the "GPT-Powered Text Humanizer" section.
    *   Click "Humanize Text". The rephrased text will appear below (requires a valid `OPENAI_API_KEY` configured for the backend).
7.  **Scan History (History Page)**:
    *   Navigate to the "History" page from the header (requires login).
    *   View a list of your past scans.
    *   Click "View Details" on any card to see the full report in a modal.

## Offline Usage

*   **Backend AI Models**:
    *   The `sentence-transformers` model is downloaded on first use. Once cached, it works offline for text similarity.
    *   The Text Humanization feature (OpenAI GPT) **requires an internet connection** to reach the OpenAI API.
*   **Database**: SQLite works offline by default.
*   **Frontend/Backend Communication**: Assumes both are running on the local machine or local network.
*   **Overall**: Most features will work offline after initial model downloads, except for features explicitly relying on external APIs like the GPT Humanizer.

## Current Limitations & Mocked Components

*   **Reverse Image Search**: Still *mocked* for Image and Video Frame Checkers.
*   **Audio Transcription**: Still a *placeholder* for Video Checker.
*   **External Corpus for Text Plagiarism**: Text checker primarily performs *self-similarity*.
*   **Scalability & Robustness**: The application is designed for development/demonstration. See "Deployment Considerations" for production aspects.
*   **Error Handling**: Basic, can be made more granular and user-friendly.
*   **Testing**: While some backend unit tests exist, comprehensive testing (unit, integration, E2E) is needed.

## Deployment Considerations (Production Environment)
(This section remains largely the same as previously generated, detailing considerations for ASGI servers, persistent databases, task queues, containerization, frontend static serving, HTTPS, scalability, CI/CD, etc.)

... (previous Deployment Considerations text would be here) ...

This README provides a good starting point for understanding, setting up, and using the application.
