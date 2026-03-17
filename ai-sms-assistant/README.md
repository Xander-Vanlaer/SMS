# Updated README.md

## Local SMS Emulator
This project now includes a local SMS emulator that supports bilingual (English/Swahili) replies for both weather and AI.

## New Endpoints
- **/phone**: Web UI for the local SMS emulator.
- **/sms/inbound**: Receive SMS messages.
- **/sms/send**: Send SMS messages.
- **/sms/inbox**: View incoming SMS messages.
- **/sms/outbox**: View outgoing SMS messages.
- **/sms/reset**: Reset the SMS emulator state.
- **/voice/transcribe**: Transcription service for voice inputs.
- **/voice/tts**: Text-to-speech service.
- **/voice/chat**: Voice chat service.

## Requirements
- This project now requires the following additional libraries:
  - jinja2
  - soundfile

## Docker Compose
Follow the instructions in the docker-compose.yml file to run the application in a containerized environment.
