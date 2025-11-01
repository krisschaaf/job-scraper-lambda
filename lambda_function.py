import json
import requests
from bs4 import BeautifulSoup
import yaml
from utils import send_email


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def find_jobs(config):
    found_jobs = []
    for url in config["urls"]:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            for term in config["search_terms"]:
                matches = soup.find_all(string=lambda t: t and term.lower() in t.lower())
                for match in matches:
                    link = match.find_parent("a")
                    if link and link.get("href"):
                        found_jobs.append({
                            "term": term,
                            "title": match.strip(),
                            "url": link["href"] if link["href"].startswith("http") else url + link["href"]
                        })
        except Exception as e:
            print(f"Fehler bei {url}: {e}")
    return found_jobs


def lambda_handler(event, context):
    config = load_config()
    jobs = find_jobs(config)

    if jobs:
        body = "\n\n".join([f"{j['term']} → {j['title']}\n{j['url']}" for j in jobs])
        send_email(config["email"], body)
        print(f"{len(jobs)} neue Jobs gefunden.")
    else:
        print("Keine neuen Jobs gefunden.")

    return {
        "statusCode": 200,
        "body": json.dumps({"jobs_found": len(jobs)})
    }

if __name__ == "__main__":
    lambda_handler({}, {})
