import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

from app.ai import handle_ai
from app.weather import handle_weather

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


def twiml_message(text: str) -> str:
    """Wrap text in minimal TwiML for an SMS reply."""
    safe = (text or "").strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        f"<Message>{safe}</Message>"
        "</Response>"
    )


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/")
def root():
    return PlainTextResponse(
        "AI SMS Assistant is running. POST Twilio webhooks to /twilio/sms\n"
    )


@app.post("/twilio/sms")
async def twilio_sms(request: Request):
    """Receive inbound Twilio SMS (application/x-www-form-urlencoded) and reply with TwiML."""
    form = await request.form()
    body = (form.get("Body") or "").strip()
    from_number = (form.get("From") or "").strip()

    if not body:
        return Response(
            content=twiml_message("Send a message like: weather 3 days brussels"),
            media_type="application/xml",
        )

    lower = body.lower()
    try:
        if lower.startswith("weather"):
            reply = await handle_weather(body)
        else:
            reply = await handle_ai(body, from_number=from_number)
    except Exception:
        logger.exception("Error processing SMS from %s: %r", from_number, body)
        reply = "Sorry—something went wrong while processing your request."

    return Response(content=twiml_message(reply), media_type="application/xml")
