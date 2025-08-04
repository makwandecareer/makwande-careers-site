from datetime import datetime, timedelta

def filter_jobs(
    jobs, 
    country, 
    title=None, 
    category=None, 
    min_salary=None, 
    max_salary=None,
    posted_within_days=None,
    only_open=None,
    sort_by_post_date=False
):
    country = country.strip().lower()

    filtered = [job for job in jobs if job.get("country", "").lower() == country]

    if title:
        filtered = [job for job in filtered if title.lower() in job.get("title", "").lower()]

    if category:
        filtered = [job for job in filtered if category.lower() in job.get("category", "").lower()]

    if min_salary is not None:
        filtered = [job for job in filtered if job.get("salary") and job["salary"] >= min_salary]

    if max_salary is not None:
        filtered = [job for job in filtered if job.get("salary") and job["salary"] <= max_salary]

    if posted_within_days is not None:
        cutoff = datetime.now().date() - timedelta(days=posted_within_days)
        filtered = [
            job for job in filtered
            if job.get("post_advertised_date") and job["post_advertised_date"] >= cutoff
        ]

    if only_open:
        today = datetime.now().date()
        filtered = [
            job for job in filtered
            if job.get("closing_date") and job["closing_date"] >= today
        ]

    if sort_by_post_date:
        filtered.sort(key=lambda x: x.get("post_advertised_date") or datetime.min.date(), reverse=True)

    return filtered
