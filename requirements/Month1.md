Here is the updated requirements document for Month 1.

This version formally decouples the **Ingestion Worker** (the background "service") from the **API** (the frontend interface), enabling you to demonstrate a true cloud-native microservices architecture.

---

# 📝 FLOS Microservice: Month 1 Requirements Specification (v2 - Decoupled)

## 1\. Project Goal: Cloud-Native Foundation

The goal for Month 1 is to establish a robust, decoupled infrastructure consisting of two distinct microservices: a **Public API** for data retrieval and a **Private Worker** for data ingestion, both sharing a containerized PostgreSQL database.

## 2\. Functional Requirements (FR)

### FR 1.0 Data Model Definition

The system **SHALL** define the PostgreSQL data schema to support the core operational status reports.

- **FR 1.1** The schema **SHALL** include a `status_report` table with: `report_id` (PK), `facility_id` (e.g., 'KORD'), `status_type`, `start_time`, `end_time`, `raw_notam_text`, and `last_updated` timestamp.
- **FR 1.2** Database migration scripts (using a tool like Alembic) **SHALL** be created to version-control schema changes.

### FR 2.0 Ingestion Worker Microservice (The "Service")

A standalone Python application **SHALL** be created to handle the Extraction, Transformation, and Loading (ETL) of legacy data.

- **FR 2.1** The Worker **SHALL** run independently of the API, designed to be executed as a scheduled task (e.g., AWS Fargate Task or Lambda).
- **FR 2.2** The Worker **SHALL** read from the defined mock data sources (JSON, CSV, Unstructured Text).
- **FR 2.3** The Worker **SHALL** transform raw inputs into structured `status_report` records and upsert (update or insert) them into the PostgreSQL database.
- **FR 2.4** The Worker **SHALL** log the outcome of each run (success/failure count) to stdout (for container logging).

### FR 3.0 Core API Microservice (The "Interface")

A FastAPI application **SHALL** be created to serve data to the future frontend.

- **FR 3.1** `GET /api/v1/status/` **SHALL** return a list of active status reports stored in the DB.
- **FR 3.2** `GET /api/v1/status/{report_id}` **SHALL** return details for a specific report.
- **FR 3.3** The API **SHALL** be read-only regarding the status data (it trusts the Worker to manage the data).

## 3\. Non-Functional Requirements (NFR)

### NFR 1.0 Architecture & Tech Stack

The solution **SHALL** demonstrate a "Shared Database" microservice pattern.

- **NFR 1.1** **Service A (API):** FastAPI, Python 3.10+, Uvicorn server.
- **NFR 1.2** **Service B (Worker):** Python 3.10+ scripts.
- **NFR 1.3** **Persistence:** PostgreSQL 15+.

### NFR 2.0 Containerization

Distinct Docker configurations **SHALL** be created to support independent scaling and deployment.

- **NFR 2.1** `Dockerfile.api`: Builds the lightweight web server image.
- **NFR 2.2** `Dockerfile.worker`: Builds the image containing ETL logic and scheduler dependencies.
- **NFR 2.3** `docker-compose.yml`: Orchestrates **three** containers locally: `flos-api`, `flos-worker`, and `flos-db`.

### NFR 3.0 DevOps & CI/CD

Automated pipelines **SHALL** treat the API and Worker as separate deployable artifacts.

- **NFR 3.1** The CI pipeline **SHALL** trigger on git push.
- **NFR 3.2** The pipeline **SHALL** build **two unique Docker images** (`flos-api:latest`, `flos-worker:latest`) and tag them appropriately.
- **NFR 3.3** Unit tests **SHALL** execute in parallel for both the API codebase and the Worker codebase.

### NFR 4.0 Testing

Testing strategy **SHALL** validate both synchronous and asynchronous logic.

- **NFR 4.1** **Worker Tests:** Verify that the Mock CSV/JSON parsers correctly map data to the DB schema (aim for 70% coverage).
- **NFR 4.2** **API Tests:** Verify that the endpoints return the correct HTTP 200/404 responses based on the data populated by the Worker.

---

### 🗓️ Month 1 Success Criteria (Checklist)

- [ ] **Postgres DB** running locally in Docker.
- [ ] **Worker Container** successfully runs a "job", reads the `runway_data.json` mock file, and populates the DB.
- [ ] **API Container** successfully starts and serves that data at `localhost:8000/api/v1/status`.
- [ ] **GitHub Actions (or similar)** shows green checkmarks for building both images.
