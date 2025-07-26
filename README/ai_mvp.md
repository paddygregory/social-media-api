# 📣 AI Social Media Content Generator API

## ❓ What is it?

This is a content-generating API powered by OpenAI that takes a **user prompt** and returns platform-specific content for **Twitter, LinkedIn, and Instagram**.

Users can customize the **tone** (e.g., professional, witty) and **length** (short, medium, long), with future support for platform-specific styles like **Twitter threads** or extended **LinkedIn posts**.

This project is designed for public use and aims to be lightweight and extensible — eventually powered by:

- **FastAPI** (for routing)
- **PostgreSQL** (for storing user prompts & results)
- **Celery + Redis** (for background task queueing)
- **Async-first architecture** using FastAPI’s async support

---

## 🧭 API Endpoints

### 🔹 `/generate` — `POST`
Generates content using OpenAI for each platform, based on user input.

**Request Body:**
```json
{
  "prompt": "Just launched my AI tool",
  "tone": "witty",
  "length": "short"
}

{
  "twitter": "AI just got cheeky 🤖💡 Check out my latest launch! #TechTuesday",
  "linkedin": "Excited to share the launch of my new AI productivity app...",
  "instagram": "Smarter. Faster. Fresher 🧠✨ New drop live now!",
  "engagement_optimization": "Add hashtags, tag relevant influencers"
}


🔹 /templates — GET
Returns available tone and length options. Useful for UI dropdowns or client-side validation.

Response:

json

{
  "tones": ["professional", "witty", "friendly"],
  "lengths": ["short", "medium", "long"]
}
🚫 Note: This endpoint does not generate content. It’s a metadata endpoint.

🔹 /health — GET
Basic system check for monitoring tools like UptimeRobot or Render health ping.

Response:

json
Copy
Edit
{ "status": "ok" }
