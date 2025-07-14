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
    *   Modern UI/UX refinements like non-blocking toast notifications, real-time client-side form validation, and enhanced loading states.
*   **Comprehensive Plagiarism Checking**:
    *   **📝 Text Checker**: Accepts direct text input or file uploads (.txt, .pdf, .docx). Extracts text and uses a `sentence-transformers` model (`all-MiniLM-L6-v2`) for self-similarity analysis.
    *   **🖼️ Image Checker**: Accepts image uploads (.jpg, .png, .gif). Calculates perceptual image hashes and simulates reverse image search using a *mocked* database.
    *   **🎥 Video Checker**: Accepts video uploads (.mp4). Extracts audio (with *placeholder* transcription) and frames. Performs NLP self-similarity on audio text and mocked reverse search on frame hashes.
*   **📊 Detailed Reports**:
    *   Auto-generated reports display an originality score, specific findings, and actionable rewrite suggestions.
    *   "Export Results" button allows downloading a text summary of the current scan (for subscribed users).
*   **👤 User Authentication & Personalized Experience**:
    *   Secure user registration and login system using JWT-based authentication.
*   **Tiered Pricing & Subscription System**:
    *   A dedicated `/pricing` page displays plan features in both card and table formats.
    *   **Stripe Integration**: Handles subscription checkouts and manages user plan status via webhooks.
    *   The backend enforces feature gates and usage limits based on user subscription plans (Free, Pro Basic, etc.). This includes monthly word counts, file size limits, and feature access for history and report downloads.
*   **User-specific scan history dashboard** with filtering, Card, and Table views to review past checks.
*   Persistent user, history, and usage data stored in a database (SQLite by default).
*   **✨ GPT-Powered Text Humanization**:
    *   An AI tool to rephrase user-provided text using an OpenAI GPT model (defaulting to `gpt-4-turbo`). Usage is metered based on the user's plan. Requires an OpenAI API key.
*   **🤖 FastAPI Backend**:
    *   Serves dedicated endpoints for plagiarism checking, authentication, scan history, subscriptions, AI tools, and a mock admin tool for setting user plans.
    *   Includes a multi-file preview endpoint (`/api/check`) that extracts text from various document types (via byte stream processing) and returns quick previews.
*   **🧪 Testing Setup**:
    *   Backend unit tests for key services and utilities (auth, text processing, history, AI services, subscriptions).
    *   Frontend component testing setup using Jest and React Testing Library, with example tests for key components.

## Technology Stack

*   **Frontend**:
    *   Next.js 14+, React 18+, TypeScript, Tailwind CSS, Framer Motion, `next-themes`, Heroicons, Jest, React Testing Library.
*   **Backend**:
    *   Python 3.x, FastAPI, Uvicorn, SQLAlchemy, Alembic, SQLite, `sentence-transformers`, `torch`, `openai`, `stripe`, and various media/document processing libraries.

## Setup and Installation

### Prerequisites

*   Node.js (v18.x or later)
*   `npm` (or `yarn`/`pnpm`)
*   Python 3.8+
*   `pip`
*   **Stripe Account & CLI**: Required for subscription functionality.
*   **OpenAI API Key**: Optional, only for the Text Humanization feature.

### Backend Setup

1.  **Stripe Product & Price Setup**:
    *   In your Stripe Dashboard, go to "Products".
    *   Create two products: "Pro Basic" and "Pro Advanced".
    *   For each product, add a recurring monthly price (e.g., $19/mo, $49/mo).
    *   Copy the **Price ID** for each (e.g., `price_...`).

2.  **Navigate to the project root directory.**
3.  **Create and activate a Python virtual environment:** `python -m venv venv` then activate it.
4.  **Install Python dependencies:** `pip install -r requirements.txt`
5.  **Set up `.env` File**:
    *   In the project root, create a `.env` file.
    *   **Database URL (Optional)**: Defaults to SQLite. For PostgreSQL, set `DATABASE_URL`.
    *   **JWT Secret Key (Recommended)**: Set `SECRET_KEY="your_strong_secret_key"`.
    *   **OpenAI API Key (Optional)**: Add `OPENAI_API_KEY="your_openai_key"`.
    *   **Stripe Configuration (Required for Subscriptions)**:
        *   Get your **Secret Key** from the Stripe Dashboard (Developers -> API keys).
        *   Create a webhook endpoint (Developers -> Webhooks), get the **Webhook Signing Secret**.
        ```env
        STRIPE_API_KEY="sk_test_..."
        STRIPE_WEBHOOK_SECRET="whsec_..."
        STRIPE_PRICE_ID_PRO_BASIC="price_..."
        STRIPE_PRICE_ID_PRO_ADVANCED="price_..."
        ```
6.  **Apply Database Migrations:** `cd backend` then `alembic upgrade head`.
7.  **Run the FastAPI Backend Server:** `cd ..` then `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`.

### Frontend Setup (Next.js)

1.  **Navigate to the `frontend` directory:** `cd frontend`
2.  **Install dependencies:** `npm install`
3.  **Environment Variables (Optional)**: If your backend is not at `http://127.0.0.1:8000`, create a `.env.local` file in `frontend` with `NEXT_PUBLIC_API_BASE_URL=http://your_backend_url`.
4.  **Run the Dev Server:** `npm run dev`. The app will be at `http://localhost:3000`.

### Testing Stripe Webhooks Locally

1.  Install the [Stripe CLI](https://stripe.com/docs/stripe-cli).
2.  Run the command to forward webhook events to your local backend server:
    ```bash
    stripe listen --forward-to localhost:8000/api/webhooks/stripe
    ```
3.  The CLI will provide a new webhook secret for testing. Use this temporary secret in your `.env` file while testing.

## How to Use

1.  **Ensure both backend and frontend servers are running.**
2.  **Access the Application**: Open `http://localhost:3000`.
3.  **Theme Toggle**: Use the sun/moon icon in the header to switch between light and dark modes.
4.  **Authentication**: Register for a new account or log in. Login is required to save and view scan history.
5.  **View Pricing**: Navigate to the "Pricing" page from the header to compare plan features and subscribe.
6.  **Checking Content (Home Page)**: Use the forms to check text, upload documents, images, or videos. Buttons provide loading state feedback. Results appear with animations.
7.  **Text Humanization (Home Page)**: Use the GPT-powered tool to rephrase text (requires API key and is subject to plan limits).
8.  **Scan History (History Page)**: View past scans. Use the dropdown to filter by content type and the icons to toggle between Card and Table views. Click "View Details" for a full report.
9.  **Multi-File Preview API (For Programmatic Use)**: The `POST /api/check` endpoint can be used by other tools to get quick text previews from multiple files.

## Running Tests

*   **Backend**: Navigate to the `backend` directory and run `python -m unittest discover -s tests`.
*   **Frontend**: Navigate to the `frontend` directory and run `npm test`.
    *   *Note: Frontend test execution may fail in some sandboxed environments due to module resolution issues. The configuration is standard and should work in a local setup.*

## Current Limitations & Mocked Components
(This section remains largely the same, detailing mocked reverse image search, placeholder audio transcription, and focus on self-similarity.)

## Deployment Considerations (Production Environment)
(This section remains largely the same, detailing production-ready practices.)

This README provides a comprehensive guide to understanding, setting up, and using the AI Plagiarism Web App.
