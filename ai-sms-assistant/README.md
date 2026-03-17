# AI SMS Assistant

A Dockerized Python FastAPI service that receives inbound SMS messages via Twilio, handles weather queries (OpenWeather) and general questions (AI API), and replies using TwiML.

## Features

- `POST /twilio/sms` — Twilio inbound SMS webhook
  - `weather <city>` — current-day forecast
  - `weather <n> days <city>` — multi-day forecast (1–5 days)
  - Any other text → answered by the configured AI model
- `GET /healthz` — returns `{"ok": true}`

## Example SMS commands

```
weather brussels
weather 3 days brussels
how to protect maize during drought
```

## Project layout

```
ai-sms-assistant/
  app/
    main.py       # FastAPI app, TwiML helpers
    weather.py    # OpenWeather geocoding + 5-day forecast
    ai.py         # OpenAI-compatible AI handler
  requirements.txt
  Dockerfile
  .env.example
  README.md       # this file
```

## Local setup

### 1. Copy and fill in environment variables

```bash
cp .env.example .env
# Edit .env — set at least OPENWEATHER_API_KEY and AI_API_KEY
```

### 2. Run with Docker

```bash
docker build -t ai-sms-assistant .
docker run --env-file .env -p 8080:8080 ai-sms-assistant
```

Health check:

```
http://localhost:8080/healthz
```

### 3. Expose locally with ngrok

Twilio needs a public HTTPS URL to call your webhook.

```bash
ngrok http 8080
```

ngrok prints a public URL, e.g.:

```
https://abcd-12-34-56-78.ngrok-free.app
```

Your Twilio webhook becomes:

```
https://abcd-12-34-56-78.ngrok-free.app/twilio/sms
```

### 4. Configure Twilio

1. Log in to the [Twilio Console](https://console.twilio.com).
2. Go to **Phone Numbers → Manage → Active numbers** and click your number.
3. Under **Messaging → A message comes in**:
   - Type: **Webhook**
   - Method: **POST**
   - URL: `https://<your-ngrok-url>/twilio/sms`
4. Click **Save**.

Send an SMS to your Twilio number and you should get a reply within seconds.

## Deploy to Google Cloud Run

### Prerequisites

- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated
- A GCP project with billing enabled
- Artifact Registry API enabled

### Steps

```bash
# Set your project and region
PROJECT_ID=your-gcp-project-id
REGION=europe-west1
IMAGE=gcr.io/${PROJECT_ID}/ai-sms-assistant

# Build and push
docker build -t ${IMAGE} .
docker push ${IMAGE}

# Deploy to Cloud Run
gcloud run deploy ai-sms-assistant \
  --image ${IMAGE} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars "OPENWEATHER_API_KEY=<key>,AI_API_KEY=<key>,AI_MODEL=gpt-4.1-mini"
```

Cloud Run returns a public HTTPS URL. Use it as your Twilio webhook URL (same `/twilio/sms` path).

> **Tip:** Never commit real API keys. Use Cloud Run [Secret Manager integration](https://cloud.google.com/run/docs/configuring/secrets) for production.

## Configuration reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | No | `8080` | Port the server listens on |
| `OPENWEATHER_API_KEY` | Yes | — | [OpenWeather](https://openweathermap.org/api) API key |
| `AI_PROVIDER` | No | `openai` | AI provider (`openai` only for now) |
| `AI_API_KEY` | Yes | — | API key for the AI provider |
| `AI_MODEL` | No | `gpt-4.1-mini` | Model name |
| `AI_BASE_URL` | No | `https://api.openai.com/v1/chat/completions` | OpenAI-compatible endpoint |
| `TWILIO_ACCOUNT_SID` | No | — | For future outbound SMS via REST |
| `TWILIO_AUTH_TOKEN` | No | — | For future outbound SMS via REST |
| `TWILIO_PHONE_NUMBER` | No | — | Your Twilio number |
