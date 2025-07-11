# AI Plagiarism Web App

## Overview

The AI Plagiarism Web App is a FastAPI-based application designed to detect plagiarism in various forms of content, including text, images, and videos. It utilizes a combination of NLP techniques, image processing, and video analysis to provide an originality score and detailed reports.

This project serves as a blueprint and initial implementation, with several AI components currently using placeholder or mocked logic for core functionality demonstration.

## Core Features

*   **📝 Text Checker**:
    *   Accepts direct text input or file uploads (.txt, .pdf, .docx).
    *   Extracts text from uploaded documents.
    *   Uses a `sentence-transformers` model (`all-MiniLM-L6-v2`) to perform self-similarity checks within the provided text (detects internally repetitive sentences).
    *   Includes a basic keyword check (e.g., for the word "copy").
*   **🖼️ Image Checker**:
    *   Accepts image uploads (.jpg, .png, .gif).
    *   Calculates a perceptual hash (average hash) of the image.
    *   Simulates reverse image search using a *mocked* database of image hashes to find potential sources.
*   **🎥 Video Checker**:
    *   Accepts video uploads (.mp4).
    *   Extracts audio and performs placeholder transcription.
    *   Runs self-similarity NLP checks on the transcribed audio text.
    *   Extracts a limited number of frames from the video.
    *   Calculates perceptual hashes for these frames and performs a *mocked* reverse image search.
    *   Combines audio and visual analysis for an overall assessment.
*   **📊 Comprehensive Reports**:
    *   Auto-generated reports display:
        *   An overall originality score.
        *   Detailed findings (e.g., similar sentences, matched image sources from mock DB, keyword alerts).
        *   Basic rewrite suggestions based on the findings.
*   **📁 File Upload Support**: Handles various file types for each checker.
*   **👤 User Authentication**:
    *   Secure signup and login system.
    *   JWT-based session management.
    *   (Currently uses an in-memory user store for development).
*   **🤖 AI Backend**:
    *   FastAPI backend serving the plagiarism checking logic.
    *   Modular services for text processing, NLP, image processing, and video processing.

## Technology Stack

*   **Backend**:
    *   Python 3.x
    *   FastAPI (for API development)
    *   Uvicorn (ASGI server)
    *   `sentence-transformers` (for NLP text similarity)
    *   `torch` (dependency for `sentence-transformers`)
    *   `Pillow` (for image processing)
    *   `imagehash` (for perceptual image hashing)
    *   `opencv-python` (for video frame extraction)
    *   `moviepy` (for audio extraction from video)
    *   `python-jose` & `passlib[bcrypt]` (for JWT authentication & password hashing)
    *   `pdfminer.six` (for PDF text extraction)
    *   `python-docx` (for DOCX text extraction)
*   **Frontend**:
    *   HTML5
    *   CSS3
    *   Vanilla JavaScript (for interacting with the backend)
*   **Database**:
    *   Currently uses an in-memory dictionary for user storage (suitable for development only).

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Backend Setup

1.  **Clone the repository (if applicable) or ensure all project files are in a directory.**
2.  **Navigate to the project root directory in your terminal.**
3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
4.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
5.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The first time you run the backend, it will download the `sentence-transformers` model (`all-MiniLM-L6-v2`), which requires an internet connection. Subsequent runs can be offline if the model is cached.*

6.  **Run the FastAPI backend server:**
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will typically be available at `http://127.0.0.1:8000`.

### Frontend Setup

The frontend consists of static HTML, CSS, and JavaScript files located in the `frontend/` directory.

1.  **No separate build step is required for the frontend.**
2.  You can open the `frontend/index.html` file directly in your web browser.
    *   Most modern browsers will allow this. The application uses CORS middleware on the backend to permit requests from `null` origin (which happens when opening local files) and common development server ports.

## How to Use

1.  **Access the Application**: Open `frontend/index.html` in your web browser.
2.  **Authentication**:
    *   **Signup**: If you're a new user, use the Signup form with your email and password.
    *   **Login**: If you have an account, use the Login form.
    *   Upon successful login/signup, your email will be displayed, and the checker sections will become available.
3.  **Checking Content**:
    *   **Text Input**: Paste text directly into the textarea under "Check Text" and click "Check Text".
    *   **Text File**: Click "Choose File" under "Check Text File", select a `.txt`, `.pdf`, or `.docx` file, and click "Check Text File".
    *   **Image File**: Click "Choose File" under "Check Image File", select a `.jpg`, `.png`, or `.gif` file, and click "Check Image File".
    *   **Video File**: Click "Choose File" under "Check Video File", select an `.mp4` file, and click "Check Video File". (Video processing can take longer).
4.  **Viewing Results**:
    *   The plagiarism report will appear in the "Results" section.
    *   It includes an "Originality Score", "Details & Matched Sources", and "Rewrite Suggestions".

## Offline Usage

*   **Backend**:
    *   The `sentence-transformers` model (`all-MiniLM-L6-v2`) is downloaded from Hugging Face Hub on its first use by the backend. Once downloaded and cached (usually in `~/.cache/torch/sentence_transformers/`), the backend can run without an internet connection for text similarity tasks.
    *   All other Python dependencies, once installed via `pip install -r requirements.txt`, work offline.
*   **Frontend**:
    *   The frontend is entirely client-side (HTML, CSS, JS) and does not require an internet connection to load after the files are on your local machine.
*   **Overall**: After the initial model download, the entire application (frontend + backend) can be run on a local machine without an active internet connection, provided the backend server is running and the frontend is accessed locally.

## Current Limitations & Mocked Components

*   **User Storage**: Uses an in-memory dictionary for users. Data is lost when the backend server restarts. A persistent database (e.g., PostgreSQL, SQLite) would be needed for production.
*   **Reverse Image Search**: The current reverse image search for the Image Checker and Video Frame Checker is *mocked*. It checks against a predefined dictionary of hashes in `backend/services/image_processing.py`. Real integration with services like TinEye, Google Images, or Bing Images API would be required for actual reverse searching.
*   **Audio Transcription**: Video audio transcription is currently a *placeholder* (`backend/services/video_processing.py transcribe_audio_placeholder`). It returns a fixed string. Integration with a real Speech-To-Text (STT) engine like Whisper, Google Speech-to-Text, etc., is needed for actual transcription.
*   **External Corpus for Text Plagiarism**: The text checker currently only performs *self-similarity* checks (within the document itself). True plagiarism detection against external sources (web, academic papers) would require a much more complex system involving web crawling, a large text database, and more advanced comparison algorithms.
*   **Scalability**: The current setup is for single-user local development. Production deployment would require considerations for concurrent users, task queuing for long-running AI jobs (especially video), and more robust error handling.
*   **Rewrite Suggestions**: Suggestions are very generic placeholders. A more advanced system would provide context-aware suggestions.
*   **Testing**: Automated tests (unit, integration) are minimal. Comprehensive testing is required for robust deployment.

## Deployment Considerations (Production Environment)

While this application is currently set up for local development, deploying it to a production environment would require several additional considerations:

### Backend Deployment

*   **ASGI Server**: Instead of `uvicorn`'s development server, use a production-grade ASGI server like Uvicorn managed by Gunicorn for robustness and process management.
    *   Example: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app`
*   **Database**: Replace the in-memory user store with a persistent relational database (e.g., PostgreSQL, MySQL, or even SQLite for smaller applications). This would involve:
    *   Choosing a database.
    *   Using an ORM like SQLAlchemy (often with Alembic for migrations) to define models and interact with the database.
    *   Updating authentication logic to query the database.
*   **Task Queue**: For long-running AI tasks like video processing or extensive NLP analysis on large documents, implement a task queue (e.g., Celery with Redis or RabbitMQ as a message broker). This prevents API requests from timing out and allows for background processing.
    *   Checker endpoints would submit jobs to the queue and potentially provide a way for clients to poll for results or receive notifications.
*   **Containerization**: Package the backend application (including Python, dependencies, and AI models) into a Docker container for consistent deployments and easier scaling.
    *   Models might be baked into the container, mounted as volumes, or fetched from a model store.
*   **Environment Variables**: Manage configuration (database URLs, secret keys, API keys for external services, model paths) through environment variables rather than hardcoding them (e.g., using `.env` files loaded by Pydantic settings in production).
*   **API Key Management**: If integrating real third-party APIs for reverse image search or STT, securely store and manage API keys.

### Frontend Deployment

*   **Static File Serving**: Serve the static frontend files (HTML, CSS, JS) using a dedicated web server like Nginx or a cloud storage service (e.g., AWS S3, Google Cloud Storage) often with a CDN (e.g., Cloudflare, AWS CloudFront) for better performance and caching.
*   **Build Process**: For more complex frontends (not currently the case here, but typical for React/Vue/Angular), a build step would compile, minify, and bundle assets.

### General Production Practices

*   **HTTPS**: Ensure all traffic is served over HTTPS. Use a reverse proxy like Nginx to handle SSL termination or utilize services from cloud providers.
*   **Scalability**:
    *   **Stateless Backend**: Design the backend to be stateless if possible, allowing multiple instances to run behind a load balancer.
    *   **Database Scaling**: Consider read replicas or other database scaling strategies if needed.
    *   **Model Serving**: For very high loads, AI models might be deployed as separate microservices with optimized serving frameworks (e.g., NVIDIA Triton Inference Server, TorchServe).
*   **Monitoring & Logging**: Implement comprehensive logging (e.g., ELK stack, Grafana Loki) and application performance monitoring (APM) (e.g., Sentry, Datadog, Prometheus/Grafana) to track errors, performance bottlenecks, and system health.
*   **CI/CD**: Set up a Continuous Integration/Continuous Deployment pipeline (e.g., GitHub Actions, Jenkins, GitLab CI) to automate testing and deployment.
*   **Security Hardening**:
    *   Regularly update dependencies.
    *   Implement rate limiting and input validation.
    *   Protect against common web vulnerabilities (OWASP Top 10).
    *   Securely manage secrets and credentials.
*   **Model Management**:
    *   Strategy for updating AI models in production.
    *   Versioning of models.
    *   Consider a model registry if managing many custom models.

This README provides a good starting point for understanding and using the application.
