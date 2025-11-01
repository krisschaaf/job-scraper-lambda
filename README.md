# JobScraper Lambda

**JobScraper Lambda** is a simple Python AWS Lambda function that periodically checks websites for job postings matching specified search terms and sends email notifications. Previously seen jobs are tracked to avoid duplicate notifications.  

The project uses **Python**, **AWS Lambda**, **S3** for storing seen jobs, and **SMTP (Gmail)** for sending emails.  

---

## Features

- Concurrent scraping of multiple URLs  
- Tracks new and previously seen job postings  
- Sends a single email with **two sections**:  
  1. New jobs  
  2. Already known jobs  
- Configuration via `config.yaml`  

---

## Configuration (`config.yaml`)

Create a `config.yaml` file in the project root with the following structure:

```yaml
search_terms:
  - example_term_1
  - example_term_2  
  # add as many as you need

urls:
  - https://company1.com/careers/jobs
  - https://company2.com/jobs
  - https://company3.com/career     
  # add as many as you need

email:
  sender: "your.email@gmail.com"
  recipient: "recipient@example.com"
  subject: "New Job Postings Found"
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  smtp_user: "your.email@gmail.com"
  smtp_password: "your-app-password"
````

## Notes on fields

- `search_terms`: list of keywords to look for in job titles/descriptions  
- `urls`: list of job pages to scrape  
- `email`: configuration for sending email  
- `smtp_*`: required if `use_ses: false`, for example Gmail SMTP credentials  
- Gmail requires an **App Password** if 2FA is enabled (recommended)  

---

## How it Works

1. The Lambda function loads `config.yaml` and retrieves already seen jobs from S3 (`seen_jobs.json`).  
2. It fetches all configured URLs in parallel and searches for the specified terms.  
3. Results are split into:  
   - **New jobs** (not seen before)  
   - **Already known jobs**  
4. The email body is formatted with **two clear sections** for new and old jobs.  
5. If new jobs are found, the S3 `seen_jobs.json` is updated.  

---

## Deployment Overview

- The project is packaged as a ZIP file for **AWS Lambda** (see `scripts/create_zip.sh`).
- Lambda retrieves and updates `seen_jobs.json` from **S3**.
- It is triggered daily via **CloudWatch Events**.
- Emails are sent either via **SMTP (Gmail)**.