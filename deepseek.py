import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


def extract_links(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all <a> tags with specified class and style
        links = soup.select('a.col-12.col-lg-4[style="padding-top:12px;padding-bottom:12px"]')
        
        # Extract href attributes, limit to 30 entries
        extracted_links = [link['href'] for link in links[:30] if 'href' in link.attrs]
        return extracted_links
    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return []


def extract_job_details(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_data = {
            "title": soup.select_one('h1.mt-5.mb-4.fw-bold').get_text(strip=True) if soup.select_one('h1.mt-5.mb-4.fw-bold') else None,
            "description": soup.select_one('div.col-12.col-lg-8.pe-lg-5 div.sub-font').get_text(strip=True) if soup.select_one('div.col-12.col-lg-8.pe-lg-5 div.sub-font') else None,
            "company_image": soup.select_one('img[alt="Employer logo"][width="240"][height="80"][class="d-block mx-auto mt-3 mb-2"][style="object-fit:contain"]')['src'] if soup.select_one('img[alt="Employer logo"][width="240"][height="80"][class="d-block mx-auto mt-3 mb-2"][style="object-fit:contain"]') else None,
            "company": soup.select_one('span.me-2.sub-font[style="color:#7B8589"]').get_text(strip=True) if soup.select_one('span.me-2.sub-font[style="color:#7B8589"]') else None,
            "location": ' '.join(span.get_text(strip=True) for span in soup.select('div.col-11.sub-font span[style="color:#25201F"]')) or None,
            "category": soup.select_one('span.ms-2.text-nowrap.sub-font').get_text(strip=True) if soup.select_one('span.ms-2.text-nowrap.sub-font') else None,
            "posted_date": soup.select_one('div.my-3.sub-font[style="color:#25201F"]').get_text(strip=True) if soup.select_one('div.my-3.sub-font[style="color:#25201F"]') else None,
            "apply_link": soup.select_one('a.application-button[href]')['href'] if soup.select_one('a.application-button[href]') else None
        }
        return job_data
    except requests.RequestException as e:
        print(f"Error fetching job details: {e}")
        return None


def save_jobs_to_file(jobs):
    if not jobs:
        print("No jobs to save")
        return
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"extracted_jobs_{current_date}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2)
        print(f"Successfully saved {len(jobs)} jobs to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")


def main():
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    jobs = []
    for page in range(0, 20):
        url = f"https://visasponsor.jobs/api/jobs?page={page}"
        links = extract_links(url, headers)
        for link in links:
            full_url = f"https://visasponsor.jobs{link}"
            job_data = extract_job_details(full_url, headers)
            if job_data:
                jobs.append(job_data)
    
    # Save jobs data
    save_jobs_to_file(jobs)


if __name__ == "__main__":
    main()