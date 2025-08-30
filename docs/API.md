# API Documentation

## Overview

The BHIV-Integrated Gurukul Content Platform provides a comprehensive REST API for video generation, user management, and analytics.

**Base URL**: `http://127.0.0.1:8000`

## Authentication

Most endpoints require authentication using JWT tokens.

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password"
}
```

### Using Tokens
Include the access token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Core Endpoints

### Upload Script
```http
POST /upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <script.txt>
```

### Stream Video
```http
GET /stream/{video_id}
```

### Rate Video
```http
POST /rate/{video_id}
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

rating=5&comment=Great video!
```

## System Endpoints

### Health Check
```http
GET /health
```

### Platform Metrics
```http
GET /metrics
Authorization: Bearer <token>
```

## Analytics Endpoints

### Video Analytics
```http
GET /analytics/video/{video_id}
Authorization: Bearer <token>
```

### Platform Analytics
```http
GET /analytics/platform?days=30
Authorization: Bearer <token>
```

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation.