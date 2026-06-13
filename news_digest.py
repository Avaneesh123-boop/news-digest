import feedparser
import smtplib
import schedule
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# =========================
# EMAIL CONFIGURATION
# =========================
SENDER_EMAIL = "avspancheri@gmail.com"
APP_PASSWORD = "Ava@123"
RECIPIENT_EMAIL = "avpancheri@gmail.com"

# =========================
# RSS FEEDS
# =========================
NEWS_SOURCES = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "AP News": "https://rsshub.app/apnews/topics/apf-topnews"
}

HEADLINES_PER_SOURCE = 5


def fetch_headlines():
    all_news = {}

    for source, feed_url in NEWS_SOURCES.items():
        feed = feedparser.parse(feed_url)

        headlines = []

        for entry in feed.entries[:HEADLINES_PER_SOURCE]:
            title = entry.get("title", "No Title")
            link = entry.get("link", "#")

            published = entry.get(
                "published",
                entry.get("updated", "Time unavailable")
            )

            headlines.append({
                "title": title,
                "link": link,
                "published": published
            })

        all_news[source] = headlines

    return all_news


def generate_html(news_data):
    today = datetime.now().strftime("%d %B %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h1>Daily News Digest</h1>
        <p>Date: {today}</p>
        <hr>
    """

    for source, articles in news_data.items():

        html += f"""
        <h2>{source}</h2>
        <ul>
        """

        for article in articles:
            html += f"""
            <li style="margin-bottom:10px;">
                <a href="{article['link']}">
                    {article['title']}
                </a>
                <br>
                <small>
                    Published: {article['published']}
                </small>
            </li>
            """

        html += "</ul>"

    html += """
    </body>
    </html>
    """

    return html


def send_email(html_content):
    msg = MIMEMultipart("alternative")

    msg["Subject"] = "Daily News Digest"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

    print("Email sent successfully.")


def news_job():
    try:
        print("Fetching headlines...")

        news = fetch_headlines()

        html = generate_html(news)

        send_email(html)

        print("Daily digest completed.")

    except Exception as e:
        print("Error:", e)


# =====================================
# SCHEDULE DAILY AT 07:00 AM
# =====================================
schedule.every().day.at("07:00").do(news_job)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(30)
