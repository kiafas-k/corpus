import feedparser
import newspaper


feed = feedparser.parse('http://rss.cnn.com/rss/money_news_international.rss')

feed_entries = feed.entries

for entry in feed_entries:
    print(entry.link)
