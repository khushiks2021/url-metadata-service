# URL Metadata Service

A FastAPI-based service that collects, stores, and serves metadata for any given URL, including HTTP headers, cookies, and page source. The service uses MongoDB for persistence and supports asynchronous background processing.

---

##  Features

* Collect HTTP headers, cookies, and HTML source from any URL
* Store and retrieve metadata using MongoDB
* Async background processing for improved performance
* RESTful API with automatic Swagger documentation
* Dockerized setup for easy deployment

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Database:** MongoDB
* **Async Processing:** asyncio
* **Containerization:** Docker & Docker Compose
* **Testing:** Pytest

---

## ⚡ Quick Start

### Prerequisites

* Docker & Docker Compose installed

### Run the Service

```bash
docker-compose up --build
```

* API Base URL: [http://localhost:8000](http://localhost:8000)
* Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints

### 1. Collect Metadata

**POST** `/metadata`

Collects metadata for a given URL and stores it in the database.

#### Request

```bash
curl -X POST http://localhost:8000/metadata \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### Response (201 Created)

```json
{
  "url": "https://example.com/",
  "status": "created",
  "message": "Metadata collected and stored successfully."
}
```

---

### 2. Retrieve Metadata

**GET** `/metadata?url=<URL>`

Fetches stored metadata for a given URL.

#### Request

```bash
curl "http://localhost:8000/metadata?url=https://example.com/"
```

#### Responses

* **200 OK** → Returns stored metadata (headers, cookies, page_source)
* **202 Accepted** → Metadata collection is in progress (queued)

---

### 3. Health Check

**GET** `/health`

Used to verify that the service is running.

---

## 🧪 Running Tests

```bash
pip install -r requirements.txt
pytest
```

---

## 🏗️ Project Structure

```
app/
├── routes/      # API endpoint definitions (transport layer)
├── services/    # Business logic (fetching URLs, DB operations)
├── worker/      # Background async tasks
├── models/      # Pydantic models (validation & serialization)
└── config.py    # Environment-based configuration
```

---

## ⚙️ Environment Variables

| Variable        | Default                   | Description                    |
| --------------- | ------------------------- | ------------------------------ |
| MONGODB_URI     | mongodb://localhost:27017 | MongoDB connection string      |
| MONGODB_DB_NAME | url_metadata              | Database name                  |
| REQUEST_TIMEOUT | 15.0                      | HTTP request timeout (seconds) |

---

## 🧩 How It Works

1. User submits a URL via `POST /metadata`
2. Service fetches HTTP response (headers, cookies, HTML)
3. Data is stored in MongoDB
4. If processing takes time, it is handled asynchronously
5. User retrieves data using `GET /metadata`

---

## 📌 Notes

* URLs are normalized before storage
* Duplicate requests are handled efficiently
* Background processing ensures non-blocking API responses

---

