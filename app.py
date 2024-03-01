from flask import Flask, Response
import feedparser
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

app = Flask(__name__)

# The URL of the original FitGirl Repacks RSS feed
rss_url = 'https://fitgirl-repacks.site/feed/'

def generate_rss_feed():
    feed = feedparser.parse(rss_url)

    def extract_magnet_links(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('magnet:?')]

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "An RSS feed Filtering out magnet links from FitGirl Repacks."
    ET.SubElement(channel, "link").text = "http://localhost:5000/"
    ET.SubElement(channel, "description").text = "An RSS feed Filtering out magnet links from FitGirl Repacks."

    for entry in feed.entries:
        if 'content' in entry:
            content = entry.content[0].value
        else:
            content = entry.summary

        magnet_links = extract_magnet_links(content)
        for magnet_link in magnet_links:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = entry.title
            ET.SubElement(item, "link").text = magnet_link
            ET.SubElement(item, "description").text = f"Magnet Link: {magnet_link}"

    return ET.tostring(rss, encoding='unicode')

@app.route("/")
def rss_feed():
    rss_feed_content = generate_rss_feed()
    return Response(rss_feed_content, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(debug=True)
