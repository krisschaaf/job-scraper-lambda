from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import requests
from bs4 import BeautifulSoup
import yaml
from utils import send_email, format_email_body
import boto3

BUCKET = "job-scraper-seen-jobs"
KEY = "seen_jobs.json"

s3 = boto3.client("s3")

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def load_seen_jobs():
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=KEY)
        return set(json.load(obj['Body']))
    except s3.exceptions.NoSuchKey:
        return set()

def save_seen_jobs(jobs):
    s3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(list(jobs), indent=2))


def fetch_url(url, search_terms):
    jobs_found = []
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for term in search_terms:
            matches = soup.find_all(string=lambda t: t and term.lower() in t.lower())
            for match in matches:
                link = match.find_parent("a")
                if link and link.get("href"):
                    job_url = link["href"] if link["href"].startswith("http") else url + link["href"]
                    jobs_found.append({
                        "term": term,
                        "title": match.strip(),
                        "url": job_url
                    })
    except Exception as e:
        print(f"Fehler bei {url}: {e}")
    return jobs_found


def find_jobs_parallel(config):
    found_jobs = []
    urls = config["urls"]
    search_terms = config["search_terms"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_url, url, search_terms): url for url in urls}

        for future in as_completed(futures):
            result = future.result()
            found_jobs.extend(result)

    return found_jobs

# --- Lambda Handler ---

def lambda_handler(event=None, context=None):
    config = load_config()
    seen_jobs = load_seen_jobs()
    found_jobs = find_jobs_parallel(config)

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