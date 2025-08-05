jobs_by_country = {
    "South Africa": [],
    "Botswana": [],
    "Namibia": [],
    "Zimbabwe": [],
    "Zambia": [],
    "Lesotho": [],
    "Mozambique": [],
    "Malawi": []
}

# After scraping per country:
jobs_by_country["South Africa"] = scrape_linkedin("South Africa")
jobs_by_country["Botswana"] = scrape_pnet("Botswana")
# and so on...


# Print summary
total_jobs = 0
for country, jobs in jobs_by_country.items():
    print(f"{country}: {len(jobs)} jobs")
    total_jobs += len(jobs)

print(f"✅ Total scraped jobs today: {total_jobs}")




