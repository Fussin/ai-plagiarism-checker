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
*   **Comprehensive Plagiarism Checking**:
    *   **📝 Text Checker**: Accepts direct text input or file uploads (.txt, .pdf, .docx). Extracts text and uses a `sentence-transformers` model (`all-MiniLM-L6-v2`) for self-similarity analysis.
    *   **🖼️ Image Checker**: Accepts image uploads (.jpg, .png, .gif). Calculates perceptual image hashes and simulates reverse image search using a *mocked* database.
    *   **🎥 Video Checker**: Accepts video uploads (.mp4). Extracts audio (with *placeholder* transcription) and frames. Performs NLP self-similarity on audio text and mocked reverse search on frame hashes.
*   **📊 Detailed Reports**:
    *   Auto-generated reports display an originality score, specific findings (e.g., similar sentences, matched image sources from mock DB), and actionable rewrite suggestions.
    *   "Export Results" button allows downloading a text summary of the current scan.
*   **👤 User Authentication & Personalized Experience**:
    *   Secure user registration and login system using JWT-based authentication.
    *   User-specific scan history dashboard to review past checks and their detailed results.
    *   Persistent user and history data stored in a database (SQLite by default).
*   **✨ GPT-Powered Text Humanization**:
    *   An AI tool to rephrase user-provided text using an OpenAI GPT model (defaulting to `gpt-4-turbo`), making it sound more natural and human-written. Requires an OpenAI API key.
*   **🤖 FastAPI Backend**:
    *   Serves dedicated endpoints for plagiarism checking (text, file, image, video), user authentication, scan history, and AI tools (like text humanization).
    *   Includes a multi-file preview endpoint (`/api/check`) that extracts text from various document types (via byte stream processing) and returns quick previews.
    *   Modular services for text processing (filepath and byte-based), NLP, image analysis, and video processing.

## Technology Stack

*   **Frontend**:
    *   Next.js 14+ (App Router)
    *   React 18+
    *   TypeScript
    *   Tailwind CSS
    *   Framer Motion (for animations and page transitions)
    *   `next-themes` (for dark/light mode theme management)
    *   Heroicons (for UI icons)
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
    *   `pdfminer.six` (for PDF text extraction from filepaths and bytes)
    *   `python-docx` (for DOCX text extraction from filepaths and bytes)
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
    *Note: This installation includes `torch`, which can be large. If you encounter "No space left on device" errors in very constrained environments, ensure adequate disk space or consider if a CPU-only version of torch is sufficient if not using local GPU acceleration for sentence-transformers (though sentence-transformers typically runs fine on CPU).*
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
    *   **Register**: Create a new account via the "Register" page.
    *   **Login**: Log in with your credentials.
    *   The header will update to show your email and a "Logout" button. Login is required to save scan history and view the History page.
5.  **Checking Content (Home Page)**:
    *   **Text Input**: Paste text directly into the "Check Text Content" section and click "Check Text".
    *   **File Uploads**: Use the "Upload & Check Files" section. Select a file for Text Documents (PDF, DOCX, TXT), Images (JPG, PNG, GIF), or Videos (MP4), then click the corresponding "Check" button.
    *   Scan results (originality score, details, suggestions) will appear in the "Scan Results" section.
    *   Click "Export Results" to download a text summary of the current scan.
6.  **Text Humanization (Home Page)**:
    *   Paste text into the "GPT-Powered Text Humanizer" section.
    *   Click "Humanize Text". The rephrased text will appear below. (Requires a valid `OPENAI_API_KEY` configured for the backend).
7.  **Scan History (History Page)**:
    *   Navigate to the "History" page from the header (requires login).
    *   View a list of your past scans, displayed as cards.
    *   Click "View Details" on any card to see the full report in a modal.
8.  **Multi-File Preview API Endpoint (For Programmatic Use)**:
    *   The `POST /api/check` endpoint can be used by other tools/scripts. It accepts multiple files and returns a JSON list containing the filename, content type, and a text preview (first 500 characters for text documents, or a type placeholder for media files) for each file.

## Offline Usage

*   **Backend AI Models**:
    *   The `sentence-transformers` model (`all-MiniLM-L6-v2`) is downloaded by the backend on its first use. Once downloaded and cached (usually in `~/.cache/torch/sentence_transformers/`), it works offline for text similarity tasks.
    *   The Text Humanization feature (using OpenAI GPT) **requires an active internet connection** to reach the OpenAI API.
*   **Database**: The default SQLite database (`test.db`) works entirely offline.
*   **Frontend & Backend Communication**: Assumes both are running on the local machine or within a local network.
*   **Overall**: Most features of the application will work offline after the initial `sentence-transformers` model download, with the notable exception of the GPT Text Humanization feature.

## Current Limitations & Mocked Components

*   **Reverse Image Search**: The reverse image search functionality within the Image Checker and Video Frame Checker is currently *mocked*. It uses a predefined dictionary of image hashes (`backend/services/image_processing.py`) rather than querying live web search APIs.
*   **Audio Transcription**: Video audio transcription is a *placeholder* (`backend/services/video_processing.py transcribe_audio_placeholder`). It returns a fixed string instead of actual transcribed audio. Integration with a real Speech-To-Text (STT) engine (e.g., OpenAI Whisper, Google Speech-to-Text) is required for this feature to be functional.
*   **External Corpus for Text Plagiarism**: The primary text checker focuses on *self-similarity* (finding highly similar sentences within the submitted document itself). True plagiarism detection against a vast external corpus (web content, academic papers) is a significantly more complex task and is not implemented.
*   **Scalability & Robustness**: The current setup is primarily for development and demonstration. Production deployment would require further considerations (see "Deployment Considerations").
*   **Error Handling**: While basic error handling is in place, it can be expanded for more specific and user-friendly feedback in various scenarios.
*   **Testing**: Backend unit tests cover key utilities and services. However, comprehensive testing, including frontend component tests and end-to-end (E2E) tests, is recommended for a production-grade application.

## Deployment Considerations (Production Environment)

While this application is set up for local development, deploying it to a production environment would require several additional considerations:

### Backend Deployment

*   **ASGI Server**: Use a production-grade ASGI server like Uvicorn managed by Gunicorn. Example: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app`
*   **Database**: Transition from SQLite to a more robust relational database like PostgreSQL or MySQL, especially for concurrent user access. This involves updating `DATABASE_URL` and ensuring the chosen Python DB driver is installed.
*   **Task Queue**: For resource-intensive AI tasks (especially video processing, extensive NLP on large documents, or numerous simultaneous OpenAI calls), implement a task queue (e.g., Celery with Redis or RabbitMQ) to handle these asynchronously, preventing API timeouts and improving responsiveness.
*   **Containerization (Docker)**: Package the backend application (Python environment, dependencies, AI models if bundled) into Docker containers for consistent deployment, easier management, and scalability.
*   **Environment Variables**: Strictly manage all configurations (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, etc.) through environment variables, not hardcoded values.
*   **API Key Security**: Ensure API keys (like OpenAI's) are securely managed and not exposed.

### Frontend Deployment (Next.js)

*   **Build for Production**: Use `npm run build` to create an optimized production build of the Next.js application.
*   **Hosting**: Deploy the output (typically in the `.next` folder after build) to a suitable hosting platform for Next.js applications (e.g., Vercel, Netlify, AWS Amplify, or a Node.js server environment).
*   **Environment Variables**: Configure `NEXT_PUBLIC_API_BASE_URL` appropriately for the production backend URL during the build process or via hosting platform environment settings.

### General Production Practices

*   **HTTPS**: Ensure all traffic is served over HTTPS.
*   **Scalability**: Consider load balancing for multiple backend instances if needed.
*   **Monitoring & Logging**: Implement robust logging and application performance monitoring (APM).
*   **CI/CD**: Set up a Continuous Integration/Continuous Deployment pipeline.
*   **Security**: Regular dependency updates, input validation, protection against common web vulnerabilities.
*   **Model Management**: Strategies for updating and versioning AI models.

This README provides a comprehensive guide to understanding, setting up, and using the AI Plagiarism Web App.
