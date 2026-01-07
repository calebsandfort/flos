# 📝 FLOS Microservice: Month 2 Requirements Specification (v4 - Hybrid System)

## 1. Project Goal: Hybrid Ingestion, Admin Controls & Event-Driven Signaling

The goal for Month 2 is to deploy a dual-purpose **Next.js** interface that supports both real-time controller monitoring and administrative manual entry. The system will leverage **Amazon SQS** to decouple updates and **AWS CDK** for automated provisioning.

## 2. Functional Requirements (FR)

### FR 4.0 Next.js Interface (The "Frontend")

- **FR 4.1 Controller Dashboard:** A read-only, high-performance grid of facility statuses using **ShadCN UI**.
- **FR 4.2 Admin Entry Page:** A new route `/admin` containing a validated form to manually create status reports.
  - **Components:** `Form`, `Select` (for Facility/Type), `Input` (for details), and `DateTimePicker`.
  - **Validation:** Form SHALL use **Zod** for schema validation (e.g., Facility ID must be a 4-letter ICAO code).
- **FR 4.3 UI Aesthetic:** Interface SHALL adhere to "Aviation Dark Mode" (Slate-950 background) for maximum legibility.

### FR 5.0 Event-Driven Messaging (SQS)

- **FR 5.1 Legacy Signaling:** The Ingestion Worker SHALL publish a message to SQS after processing legacy files.
- **FR 5.2 Manual Signaling:** The API Service SHALL publish an identical SQS message after a manual entry is saved.
- **FR 5.3 Unified Payload:** The JSON message SHALL contain:
  ```json
  {
    "report_id": "uuid",
    "facility_id": "KORD",
    "status_type": "RUNWAY_CLOSURE",
    "created_by": "ADMIN_USER",
    "timestamp_utc": "2025-12-23T14:30:00Z"
  }
  ```

### FR 6.0 Database & API Enhancements

- **FR 6.1 Audit Column:** The `status_report` table SHALL include a `created_by` column (String) to distinguish between `SYSTEM_WORKER` and `ADMIN_USER`.
- **FR 6.2 POST Endpoint:** The API SHALL expose `POST /api/v1/status/` to handle authenticated manual entries.

## 3. Non-Functional Requirements (NFR)

### NFR 5.0 Infrastructure as Code (AWS CDK)

- **NFR 5.1 SQS Construct:** Provision a standard SQS queue with a Dead Letter Queue (DLQ) for failed messages.
- **NFR 5.2 IAM Roles:** The Worker and API services SHALL be granted `sqs:SendMessage` permissions via CDK.
- **NFR 5.3 Networking:** LocalStack integration SHALL be used in `docker-compose` to mock SQS during local development.

### NFR 6.0 Performance & Accessibility

- **NFR 6.1 SSR:** Next.js Server Components SHALL be used to fetch initial dashboard data for sub-second page loads.
- **NFR 6.2 508 Compliance:** Components SHALL use **Radix UI** primitives (via ShadCN) to ensure screen reader accessibility.

---

### 🗓️ Month 2 Success Criteria (Checklist)

- [ ] **Admin Entry:** I can submit a manual report via `/admin` and see it appear on the Dashboard.
- [ ] **Data Lineage:** The `created_by` column in the database accurately reflects the source.
- [ ] **Messaging:** Both the API and Worker successfully push messages to **LocalStack** SQS.
- [ ] **Infrastructure:** `cdk deploy` successfully sets up the SQS Queue and Frontend ALB.
