import asyncio
from app.weather import handle_weather
from app.ai import handle_ai, translate_to_swahili

async def handle_user_input(text, from_number):
    if "weather" in text.lower():
        weather_response = await handle_weather(text)
        return f'EN: {weather_response}\n\nSW: {await translate_to_swahili(weather_response)}'
    else:
        ai_response = await handle_ai(text)
        return f'EN: {ai_response}\n\nSW: {await translate_to_swahili(ai_response)}'