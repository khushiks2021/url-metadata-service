# URL Metadata Service
---

This service allows you to submit a URL and retrieve its metadata on demand. If the data isn’t available yet, the request is processed in the background without blocking the API.

---

## Getting Started

### Prerequisites

* Docker
* Docker Compose

### Run Locally

```bash
docker-compose up --build
```

Once running:

* API: http://localhost:8000
* Docs: http://localhost:8000/docs

---

## API Endpoints

### Create Metadata

**POST** `/metadata`

Triggers metadata collection for a given URL.

```bash
curl -X POST http://localhost:8000/metadata \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response (201):**

```json
{
  "url": "https://example.com/",
  "status": "created",
  "message": "Metadata collected and stored successfully."
}
```

---

### Get Metadata

**GET** `/metadata?url=<URL>`

Fetch metadata for a URL.

* **200 OK** → Metadata available
* **202 Accepted** → Processing in progress

```bash
curl "http://localhost:8000/metadata?url=https://example.com/"
```

---

### Health Check

**GET** `/health`

Simple endpoint to verify service availability.

---

## Running Tests

```bash
pip install -r requirements.txt
pytest
```

---

## Project Structure

```
app/
├── routes/     # API layer
├── services/   # Core logic
├── worker/     # Background tasks
├── models/     # Data models
└── config.py   # Configuration
```

---

## Configuration

| Variable        | Default                   | Description               |
| --------------- | ------------------------- | ------------------------- |
| MONGODB_URI     | mongodb://localhost:27017 | MongoDB connection string |
| MONGODB_DB_NAME | url_metadata              | Database name             |
| REQUEST_TIMEOUT | 15.0                      | Request timeout (seconds) |




