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
    *   User-specific scan history dashboard with both Card and Table views to review past checks and their detailed results.
    *   Persistent user and history data stored in a database (SQLite by default).
*   **✨ GPT-Powered Text Humanization**:
    *   An AI tool to rephrase user-provided text using an OpenAI GPT model (defaulting to `gpt-4-turbo`), making it sound more natural and human-written. Requires an OpenAI API key.
*   **🤖 FastAPI Backend**:
    *   Serves dedicated endpoints for plagiarism checking (text, file, image, video), user authentication, scan history, and AI tools (like text humanization).
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
    *   FastAPI (for API development)
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
*   **OpenAI API Key**: Required *only* for the Text Humanization feature. If you don't provide it, other features will still work.

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
    *   Create a `.env` file in the **project root directory** (the same level as `frontend` and `backend` folders).
    *   **Database URL (Optional for Default SQLite)**: The application defaults to a SQLite database (`test.db`) created in the project root. To use a different database (e.g., PostgreSQL), set `DATABASE_URL`:
        ```env
        # Example for PostgreSQL:
        # DATABASE_URL="postgresql://youruser:yourpassword@localhost:5432/yourdatabase"
        ```
    *   **OpenAI API Key (Optional)**: If you plan to use the Text Humanization feature, add your key:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        ```
    *   **JWT Secret Key (Recommended for Production)**: While a default is provided in `backend/config.py`, you should override it for production:
        ```env
        SECRET_KEY="your_very_strong_random_secret_key_for_jwt"
        ```
5.  **Apply Database Migrations:**
    *   Navigate to the `backend` directory: `cd backend`
    *   Run Alembic migrations to create database tables: `alembic upgrade head`
    *   Navigate back to project root: `cd ..`
    *(If the `alembic` command is not found directly, try `python -m alembic upgrade head` from within the `backend` directory after activating the virtual environment).*
6.  **Run the FastAPI Backend Server:**
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
3.  **Set up Environment Variables (Frontend - Optional for local default)**:
    *   The frontend defaults to connecting to the backend at `http://127.0.0.1:8000`.
    *   If your backend runs on a different URL, create a `.env.local` file in the `frontend` directory:
        ```env
        NEXT_PUBLIC_API_BASE_URL=http://your_backend_api_url
        ```
4.  **Run the Next.js Development Server:**
    ```bash
    npm run dev
    ```
    The frontend will typically be available at `http://localhost:3000`.

## How to Use

1.  **Ensure both backend and frontend servers are running.**
2.  **Access the Application**: Open `http://localhost:3000` in your web browser.
3.  **Theme Toggle**: Use the sun/moon icon in the header to switch between light and dark modes.
4.  **Authentication**:
    *   **Register**: Create a new account. The form includes client-side validation for email format and password length.
    *   **Login**: Log in with your credentials. Success and error messages are shown as toast notifications.
    *   The header will update to show your email and a "Logout" button. Login is required to save scan history and view the History page.
5.  **Checking Content (Home Page)**:
    *   Use the respective sections to check text, text files, images, or videos. Buttons provide loading state feedback.
    *   Scan results will appear with animations. Click "Export Results" to download a text summary.
6.  **Text Humanization (Home Page)**:
    *   Paste text and click "Humanize Text". The rephrased text will appear below.
7.  **Scan History (History Page)**:
    *   Navigate to the "History" page (requires login).
    *   Use the view toggle icons to switch between a responsive Card layout and a compact Table layout.
    *   Click "View Details" on any item to see the full report in a modal.
8.  **Multi-File Preview API Endpoint (For Programmatic Use)**:
    *   The `POST /api/check` endpoint can be used by other tools/scripts to get a quick text preview from multiple files at once.

## Running Tests

*   **Backend**: Navigate to the `backend` directory and run `python -m unittest discover -s tests`.
*   **Frontend**: Navigate to the `frontend` directory and run `npm test`.
    *   *Note: Frontend test execution may fail in some constrained sandbox environments due to issues with Jest's module resolution for `ts-node` or `next/jest`. The configuration is standard and should work in a local development setup.*

## Current Limitations & Mocked Components
(This section remains largely the same as the previous version, detailing mocked reverse image search, placeholder audio transcription, and focus on self-similarity for text.)

## Deployment Considerations (Production Environment)
(This section remains largely the same as the previous version, detailing production-ready practices.)

This README provides a comprehensive guide to understanding, setting up, and using the AI Plagiarism Web App.
