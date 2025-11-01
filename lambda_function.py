import json
import os
import requests
from bs4 import BeautifulSoup
import yaml
from utils import send_email, format_email_body

SEEN_FILE = "seen_jobs.json"


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def load_seen_jobs():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(jobs):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(jobs), f, indent=2)


def find_jobs(config):
    found_jobs = []
    for url in config["urls"]:
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            for term in config["search_terms"]:
                matches = soup.find_all(string=lambda t: t and term.lower() in t.lower())
                for match in matches:
                    link = match.find_parent("a")
                    if link and link.get("href"):
                        job_url = link["href"] if link["href"].startswith("http") else url + link["href"]
                        found_jobs.append({
                            "term": term,
                            "title": match.strip(),
                            "url": job_url
                        })
        except Exception as e:
            print(f"Fehler bei {url}: {e}")
    return found_jobs


def lambda_handler(event=None, context=None):
    config = load_config()
    seen_jobs = load_seen_jobs()
    found_jobs = find_jobs(config)

    all_urls = {j["url"] for j in found_jobs}
    new_jobs = [j for j in found_jobs if j["url"] not in seen_jobs]
    old_jobs = [j for j in found_jobs if j["url"] in seen_jobs]

    if new_jobs:
        seen_jobs.update(all_urls)
        save_seen_jobs(seen_jobs)

    if found_jobs:
        body = format_email_body(new_jobs, old_jobs)
        send_email(config["email"], body)
        print(f"E-Mail gesendet: {len(new_jobs)} neu, {len(old_jobs)} bekannt.")
    else:
        print("Keine Jobs gefunden.")

    return {"statusCode": 200, "new_jobs": len(new_jobs), "known_jobs": len(old_jobs)}


if __name__ == "__main__":
    lambda_handler()