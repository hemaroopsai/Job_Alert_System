import os
import requests
import time
from twilio.rest import Client
import json

# ---------------- CONFIG ----------------
# --- Secrets (Loaded from Environment Variables) ---
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWilio_AUTH = os.environ.get("TWilio_AUTH")
TO_WHATSAPP = os.environ.get("TO_WHATSAPP")
TWILIO_WHATSAPP = os.environ.get("TWILIO_WHATSAPP", "whatsapp:+14155238886")

# --- Settings ---
LOCATION = "Hyderabad, India"
SEARCH_QUERIES = ["AI ML fresher jobs", "Python fresher jobs", "Data Scientist fresher jobs"]
JOB_LIMIT_PER_QUERY = 7
HISTORY_FILE = "sent_jobs.log"
JOB_SITES = [
    "linkedin.com/jobs",
    "naukri.com",
    "indeed.com",
    "glassdoor.co.in",
    "wellfound.com", # Formerly AngelList
    "instahyre.com"
]
# ----------------------------------------

def load_sent_jobs():
    """Loads the history of sent job links from a file."""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        print("History file not found. Starting fresh.")
        return set()

def save_sent_jobs(links):
    """Appends new links to the history file."""
    with open(HISTORY_FILE, 'a') as f:
        for link in links:
            f.write(link + '\n')

def fetch_jobs():
    """Fetches ONLY NEW job postings."""
    print("Fetching job postings...")
    sent_jobs = load_sent_jobs()
    print(f"Loaded {len(sent_jobs)} previously sent jobs from history.")
    
    messages_to_process = []
    serper_url = "https://google.serper.dev/search"
    site_query = " OR ".join([f"site:{site}" for site in JOB_SITES])
    
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    for query in SEARCH_QUERIES:
        full_query = f"{query} in {LOCATION} {site_query}"
        payload = json.dumps({"q": full_query})

        try:
            response = requests.post(serper_url, headers=headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            new_jobs_found = []
            if "organic" in results and results["organic"]:
                for job in results["organic"]:
                    link = job.get('link')
                    if link and link not in sent_jobs:
                        title = job.get('title', 'No Title Available')
                        new_jobs_found.append({"title": title, "link": link})
            
            if new_jobs_found:
                print(f"Found {len(new_jobs_found)} new jobs for query: '{query}'")
                job_links_text = []
                new_links_to_save = []
                
                for job in new_jobs_found[:JOB_LIMIT_PER_QUERY]:
                    job_links_text.append(f"*{job['title']}*\n{job['link']}")
                    new_links_to_save.append(job['link'])
                    
                query_header = f"✨ {len(new_links_to_save)} New Jobs for '{query}':\n"
                full_message_body = query_header + "\n\n".join(job_links_text)
                
                messages_to_process.append({
                    "message": full_message_body,
                    "links_to_save": new_links_to_save
                })
            else:
                 print(f"No new jobs found for query: '{query}'")

        except requests.exceptions.RequestException as e:
            print(f"API Error fetching jobs for '{query}': {e}")

    return messages_to_process

def send_whatsapp(client, message_body):
    """Sends a single WhatsApp message."""
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP, body=message_body, to=TO_WHATSAPP)
        print(f"WhatsApp message sent successfully! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return False

def main():
    """Main function to run the job task once."""
    if not all([SERPER_API_KEY, TWILIO_SID, TWILIO_AUTH, TO_WHATSAPP]):
        print("Error: Missing one or more required environment variables. Exiting.")
        return

    client = Client(TWILIO_SID, TWILIO_AUTH)
    
    print("\n--- Running job runner ---")
    messages_to_process = fetch_jobs()
    
    if not messages_to_process:
        print("No new job updates to send.")
    else:
        for i, item in enumerate(messages_to_process):
            print(f"Sending message {i+1}/{len(messages_to_process)}...")
            if send_whatsapp(client, item["message"]):
                save_sent_jobs(item["links_to_save"])
                print(f"Saved {len(item['links_to_save'])} new links to history.")
            if i < len(messages_to_process) - 1:
                time.sleep(3)
            
    print("--- Job runner finished ---")

if __name__ == "__main__":
    main()