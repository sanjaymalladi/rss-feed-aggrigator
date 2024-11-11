from flask import Flask, Response
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# List of RSS feed URLs
rss_urls = [
    "https://venturebeat.com/category/ai/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.reddit.com/r/artificial/.rss",
    "https://deepmind.com/blog/rss.xml",
    "https://googleaiblog.blogspot.com/atom.xml",
    "https://web.mit.edu/newsoffice/topic/mitcomputers-rss.xml",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index"
]

def generate_rss():
    # Create the root RSS element
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    # Add channel metadata
    ET.SubElement(channel, "title").text = "Aggregated AI News Feed"
    ET.SubElement(channel, "link").text = "https://rss-feed-aggrigator.onrender.com/rss"  # Update with your domain when deployed
    ET.SubElement(channel, "description").text = "An aggregated RSS feed from multiple AI news sources"
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    # Fetch and parse each RSS feed, then add each item to the combined feed
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                item = ET.SubElement(channel, "item")
                ET.SubElement(item, "title").text = entry.title
                ET.SubElement(item, "link").text = entry.link
                ET.SubElement(item, "description").text = entry.get("description", "No description available")
                
                # Handle pubDate
                pub_date = entry.get("published", None)
                if not pub_date and "published_parsed" in entry:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime("%a, %d %b %Y %H:%M:%S +0000")
                else:
                    pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
                ET.SubElement(item, "pubDate").text = pub_date
                
                # GUID (unique link)
                ET.SubElement(item, "guid").text = entry.link
                
                # Handle images
                if "media_thumbnail" in entry:
                    image_url = entry.media_thumbnail[0]["url"]
                    image_data = requests.get(image_url).content
                    image = Image.open(BytesIO(image_data))
                    image.save(f"static/images/{os.path.basename(image_url)}")
                    ET.SubElement(item, "enclosure").set("url", f"/static/images/{os.path.basename(image_url)}")
        except Exception as e:
            print(f"Error processing feed {url}: {e}")
            continue
    
    # Convert the XML tree to a string and return it as a response
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)

@app.route("/rss")
def rss_feed():
    rss_xml = generate_rss()
    return Response(rss_xml, mimetype='application/rss+xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
