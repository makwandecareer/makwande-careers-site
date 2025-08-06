import os
from datetime import datetime

# Your site URL
BASE_URL = "https://autoapply-api.onrender.com"

# Folder where HTML files are stored
HTML_DIR = "."

# XML Header
sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

# Loop through files and add to sitemap
for root, dirs, files in os.walk(HTML_DIR):
    for file in files:
        if file.endswith(".html"):
            path = os.path.relpath(os.path.join(root, file), HTML_DIR)
            url = f"{BASE_URL}/{path.replace(os.sep, '/')}"
            lastmod = datetime.utcnow().strftime("%Y-%m-%d")
            sitemap.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>")

# Close XML
sitemap.append('</urlset>')

# Write to sitemap.xml
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(sitemap))

print("✅ sitemap.xml generated successfully!")
