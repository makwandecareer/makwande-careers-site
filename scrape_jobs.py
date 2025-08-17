import csv, argparse, sys, datetime as dt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="jobs.csv")
    args = ap.parse_args()

    # TODO: replace this with your real scraping logic.
    # For now we produce a tiny sample so the pipeline proves out.
    rows = [
        {
            "title": "Software Engineer",
            "company": "Example Corp",
            "location": "Remote",
            "description": "Build and ship things.",
            "apply_url": "https://example.com/jobs/1",
            "country": "ZA",
            "remote": "true",
            "closing_date": "",
            "posted_at": dt.datetime.utcnow().isoformat(timespec="seconds"),
        },
        {
            "title": "Data Analyst",
            "company": "Sample Ltd",
            "location": "Johannesburg",
            "description": "Analyze data and create dashboards.",
            "apply_url": "https://example.com/jobs/2",
            "country": "ZA",
            "remote": "false",
            "closing_date": "",
            "posted_at": dt.datetime.utcnow().isoformat(timespec="seconds"),
        },
    ]

    headers = ["title","company","location","description","apply_url",
               "country","remote","closing_date","posted_at"]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {len(rows)} rows to {args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())


