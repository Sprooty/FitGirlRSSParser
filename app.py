from flask import Flask, Response
import feedparser
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import json

app = Flask(__name__)

# The URL of the original FitGirl Repacks RSS feed
rss_url = 'https://fitgirl-repacks.site/feed/'

# Paths for cache files
cache_path = 'feed_cache.xml'
magnet_links_path = 'magnet_links.json'

def fetch_and_cache_feed():
    feed = feedparser.parse(rss_url)
    with open(cache_path, 'w') as file:
        json.dump(feed, file)
    return feed

def load_cached_feed():
    if os.path.exists(cache_path):
        with open(cache_path) as file:
            return json.load(file)
    else:
        return None

def update_magnet_links_cache(new_links):
    if os.path.exists(magnet_links_path):
        with open(magnet_links_path) as file:
            existing_links = json.load(file)
    else:
        existing_links = []

    updated = False
    for link in new_links:
        if link not in existing_links:
            existing_links.append(link)
            updated = True

    if updated:
        with open(magnet_links_path, 'w') as file:
            json.dump(existing_links, file)

    return existing_links

def generate_rss_feed(feed):
    def extract_magnet_links(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('magnet:?')]

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Custom RSS feed for FitGirl Repacks."
    ET.SubElement(channel, "link").text = "http://localhost:5000/"
    ET.SubElement(channel, "description").text = "Custom RSS feed for FitGirl Repacks."

    all_magnet_links = []
    for entry in feed['entries']:
        content = entry.get('content', [{}])[0].get('value', entry.get('summary', ''))
        magnet_links = extract_magnet_links(content)
        all_magnet_links.extend(magnet_links)

    unique_magnet_links = update_magnet_links_cache(all_magnet_links)

    for magnet_link in unique_magnet_links:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = "Magnet Link"
        ET.SubElement(item, "link").text = magnet_link
        ET.SubElement(item, "description").text = f"Magnet Link: {magnet_link}"

    return ET.tostring(rss, encoding='unicode')

@app.route("/")
def rss_feed():
    try:
        feed = fetch_and_cache_feed()
    except Exception as e:
        feed = load_cached_feed()
        if feed is None:
            return "Error fetching feed and no cache available.", 500

    rss_feed_content = generate_rss_feed(feed)
    return Response(rss_feed_content, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(debug=True)
