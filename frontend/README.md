# DocDive

## Project Overview

DocDive is an advanced LLM-powered document search and Q&A platform that enables users to dive deep into their documents to extract meaningful insights and answers. This repository contains the frontend application built with React, TypeScript, and Tailwind CSS.

## Features

- **Document Upload**: Upload and manage PDF, Markdown, CSV, and text documents
- **Document Browser**: Search and filter uploaded documents
- **Q&A Interface**: Query your documents with natural language
- **Analytics Dashboard**: View performance metrics and system health
- **Responsive Design**: Works on both desktop and mobile devices

## Technology Stack

This project is built with:

- Vite - Fast, modern frontend build tool
- TypeScript - Type-safe JavaScript
- React - UI component library
- shadcn/ui - High-quality UI components
- Tailwind CSS - Utility-first CSS framework
- Axios - API client for backend communication

## Getting Started

### Prerequisites

- Node.js 20+ and npm

### Installation

1. Clone the repository
```sh
git clone https://github.com/amulyavarshney/DocDive.git
cd docdive/frontend
```

2. Install dependencies
```sh
npm install
```

3. Set up environment variables
Create a `.env` file in the frontend directory with:
```
VITE_API_URL=http://localhost:8000
```

4. Start the development server
```sh
npm run dev
```

The development server will start at http://localhost:8080 by default.

## Building for Production

To create a production build:

```sh
npm run build
```

This will generate optimized assets in the `dist` directory.

## Docker Deployment

The frontend can be deployed using Docker:

```sh
docker build -t docdive-frontend .
docker run -p 80:80 docdive-frontend
```

Or using docker-compose from the project root:

```sh
docker-compose up -d
```

## Project Structure

```
frontend/
├── public/         # Static assets
├── src/
│   ├── api/        # API client and endpoints
│   ├── components/ # Reusable UI components
│   ├── contexts/   # React context providers
│   ├── hooks/      # Custom React hooks
│   ├── lib/        # Utility functions
│   ├── pages/      # Page components
│   └── types/      # TypeScript type definitions
├── index.html      # Entry HTML file
└── vite.config.ts  # Vite configuration
```

## License

MIT
