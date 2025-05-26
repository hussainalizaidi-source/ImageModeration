# Image Moderation App with FastAPI & Hive AI

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Hive AI](https://img.shields.io/badge/Hive%20AI-4b32c3?style=for-the-badge&logo=Hive&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-0172c2?style=for-the-badge)
![Bulma](https://img.shields.io/badge/Bulma-00D1B2?style=for-the-badge&logo=bulma&logoColor=white)

A **content-moderation micro-service** that utilizes **Hive AI’s visual-moderation API** to flag or block images containing nudity, violence, extremist symbols, self-harm, or other unwanted content. Front-end pages are rendered with **Jinja2** and styled with **Bulma CSS + HTMX** for a lightweight reactive UI.

---

## Architecture Overview

| Layer          | Technology                    | Purpose                                                 |
| -------------- | ----------------------------- | ------------------------------------------------------- |
| Gateway        | **FastAPI**                   | REST endpoints, JWT auth, streaming uploads             |
| Moderation     | **Hive AI Visual Moderation** | External AI classification (NSFW, violence, hate, etc.) |
| Persistence    | **MongoDB (motor)**           | Stores API tokens & request logs                        |
| Presentation   | **Jinja2 + Bulma + HTMX**     | Minimal server-side rendered UI                         |
| Infrastructure | **Docker Compose**            | Orchestrates API & MongoDB containers                   |

### Key Features

- **Token-based authentication** with admin/non-admin roles.
- **Streaming image upload** (up to 20 MB) – no temp files.
- Detailed category breakdown & confidence scores returned by Hive.
- **Usage-tracking middleware** records endpoint + timestamp for each call.
- Fully **dockerized** for local or CI deployment.

---

## Quick Start (Docker)

Assuming you have Docker and Docker Compose installed, follow these steps to run the application using the provided `Dockerfile` and `docker-compose.yml`.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ImageModeration.git
cd ImageModeration
```

### 2. Set Up Environment
Copy the `.env.example` file to `.env` and edit it with your credentials:
```bash
cp .env.example .env
```

Edit `.env` with the following variables:
```env
HIVE_API_KEY=your_hive_api_key
MONGO_USER=admin
MONGO_PASS=password
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=moderatedb
AUTH_SOURCE=admin
```
Replace `your_hive_api_key` with your actual Hive AI API key.

### 3. Run with Docker Compose
Start the services using the provided `docker-compose.yml`:
```bash
docker compose up --build
```
- **Backend** will be available at [http://localhost:7000](http://localhost:7000)
- **API Documentation (Swagger UI)** at [http://localhost:7000/docs](http://localhost:7000/docs)

### 4. Create Initial Admin Token
Access the MongoDB container to insert an initial admin token:
```bash
docker exec -it image-moderation-mongodb-1 mongosh -u admin -p password --authenticationDatabase admin
```

In the MongoDB shell:
```javascript
use moderatedb
db.tokens.insertOne({ 
  "token": "INITIAL_ADMIN_TOKEN",  // Replace with a strong token
  "is_admin": true,
  "created_at": new Date() 
})
```
Exit the shell with `Ctrl+D`.

**Security Note:** Generate a strong token using:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Local Development (Without Docker)

If you prefer to run the application locally without Docker, follow these steps.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ImageModeration.git
cd ImageModeration
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Download Static Assets
The static assets (`bulma.min.css` and `htmx.min.js`) are sourced from CDNs. Download them to the `static` directory:
```bash
mkdir -p static
curl -o static/bulma.min.css https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css
curl -L -o static/htmx.min.js https://unpkg.com/htmx.org@1.9.5/dist/htmx.min.js
```

### 5. Run MongoDB Locally
Start MongoDB using Docker (or use an existing MongoDB instance):
```bash
docker run -d --name mongo -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:6.0
```

### 6. Set Up Environment Variables
Create a `.env` file with the necessary variables:
```env
HIVE_API_KEY=your_hive_api_key
MONGO_USER=admin
MONGO_PASS=password
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=moderatedb
AUTH_SOURCE=admin
```

### 7. Run the FastAPI Application
Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 7000
```
- Access the application at [http://localhost:7000](http://localhost:7000)

### 8. Create Initial Admin Token
Connect to MongoDB and insert the admin token:
```bash
mongosh -u admin -p password --authenticationDatabase admin
```

In the MongoDB shell:
```javascript
use moderatedb
db.tokens.insertOne({ 
  "token": "INITIAL_ADMIN_TOKEN",  // Replace with a strong token
  "is_admin": true,
  "created_at": new Date() 
})
```

---

## Project Layout

```
.
├── app
│   ├── backend
│   │   ├── routers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   └── moderator.py   # Hive moderation logic
│   │   ├── dependencies.py    # Depends helpers (token checks, DB)
│   │   └── middlewares.py     # Usage-tracking middleware
│   ├── config.py              # Pydantic settings (env vars)
│   ├── database
│   │   ├── connection.py      # Async Mongo connector (motor)
│   │   ├── crud.py            # Common DB utilities
│   │   └── models.py          # Pydantic models
│   ├── main.py                # FastAPI app factory & lifespan
│   ├── static                 # bulma.min.css & htmx.min.js
│   └── templates              # Jinja2 templates (base.html, upload.html)
├── docker-compose.yml         # Multi-service orchestration
├── Dockerfile                 # Backend container
├── requirements.txt           # Python dependencies
├── .env.example               # Sample env vars
└── README.md
```

---

## Key Commands (Docker)

| Command                                                | Description                              |
| ------------------------------------------------------ | ---------------------------------------- |
| `docker compose up --build`                            | Build and start services                 |
| `docker compose down -v`                               | Stop and remove containers and volumes   |
| `docker exec -it image-moderation-mongodb-1 mongosh ...` | Access MongoDB shell                     |
| `docker logs image-moderation-backend-1`               | View backend logs                        |

---

## Notes
- The `Dockerfile` and `docker-compose.yml` are already included in the repository, so there’s no need to create them manually.
- For local development, ensure MongoDB is running and accessible at the specified host and port.
- Always use strong, unique tokens for security purposes.
- The static assets (`bulma.min.css` and `htmx.min.js`) are downloaded from CDNs as specified in the setup steps.
