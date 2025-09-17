# Automated Job Alert Bot

This project uses Python and GitHub Actions to automatically search for new job postings and send alerts via WhatsApp.

## Features
- Searches across multiple job platforms (LinkedIn, Naukri, Indeed, etc.).
- Keeps a history to avoid sending duplicate job alerts.
- Runs on a daily schedule automatically using GitHub Actions.

## Setup
1.  Clone the repository.
2.  Create a virtual environment and install dependencies from `requirements.txt`.
3.  Set up the necessary secrets in GitHub Repository Settings > Secrets and variables > Actions.
    - `SERPER_API_KEY`
    - `TWILIO_SID`
    - `TWILIO_AUTH`
    - `TO_WHATSAPP`
    - `TWILIO_WHATSAPP`