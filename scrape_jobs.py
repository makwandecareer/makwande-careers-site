import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Query
from typing import List, Dict

scrape_router = APIRouter()

supported_countries = {
    "south_africa": {
        "pnet": "https://www.pnet.co.za/jobs?q={query}",
        "career24": "https://www.career24.com/jobs/lc-south-africa/kw-{query}/"
    },
    # Add more countries with their URLs later
}

def scrape_pnet(query: str, country: str):
    url = supported_countries[country]["pnet"].format(query=query)
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    jobs = []
    for job in soup.select('.job-item'):
        title = job.select_one('h3').text.strip() if job.select_one('h3') else "No title"
        company = job.select_one('.company-name').text.strip() if job.select_one('.company-name') else "No company"
        location = job.select_one('.location').text.strip() if job.select_one('.location') else "No location"
        link = "https://www.pnet.co.za" + job.select_one('a')['href'] if job.select_one('a') else ""
        jobs.append({
            "source": "PNet",
            "title": title,
            "company": company,
            "location": location,
            "link": link
        })
    return jobs

def scrape_career24(query: str, country: str):
    url = supported_countries[country]["career24"].format(query=query)
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    jobs = []
    for job in soup.select('.job-card'):
        title = job.select_one('h2').text.strip() if job.select_one('h2') else "No title"
        company = job.select_one('.job-company').text.strip() if job.select_one('.job-company') else "No company"
        location = job.select_one('.job-location').text.strip() if job.select_one('.job-location') else "No location"
        link = job.select_one('a')['href'] if job.select_one('a') else ""
        jobs.append({
            "source": "Career24",
            "title": title,
            "company": company,
            "location": location,
            "link": link
        })
    return jobs

@scrape_router.get("/api/scrape_jobs")
def scrape_jobs(
    query: str = Query(..., description="Search keyword"),
    country: str = Query("south_africa", description="Supported country code")
) -> List[Dict]:
    if country not in supported_countries:
        return [{"error": "Country not supported"}]

    pnet_jobs = scrape_pnet(query, country)
    career24_jobs = scrape_career24(query, country)

    return pnet_jobs + career24_jobs



