"I have attached a 16:9 UI mockup for the FLOS Dashboard. Please implement the Next.js frontend in the `/flos/frontend` directory using **ShadCN UI**.

**Instructions:**

1.  **Visual Match:** Match the layout, spacing, and 3-column grid exactly as shown in the screenshot.
2.  **Theme:** Use the provided Tailwind config variables (`atc-background`, `atc-alert`, etc.) to match the high-contrast 'Aviation Dark Mode'.
3.  **Components:** Use ShadCN `Card` for the reports, `Badge` for the status, and `Input` for the facility search.
4.  **Data:** Map the `facility_id`, `status_type`, and `raw_notam_text` from my FastAPI `GET /api/v1/status` endpoint to the cards.
5.  **Typography:** Use a monospaced font for the facility IDs and timestamps to ensure data legibility."
