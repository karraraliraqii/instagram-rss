
from flask import Flask, Response
import instaloader
from feedgen.feed import FeedGenerator
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome! Use /rss/<username> to get Instagram RSS feed."

@app.route('/rss/<username>')
def instagram_rss(username):
    try:
        L = instaloader.Instaloader(
            download=False,
            quiet=True,
            save_metadata=False,
        )

        # تسجيل الدخول إذا توفرت بيانات
        IG_USER = os.getenv("IG_USERNAME")
        IG_PASS = os.getenv("IG_PASSWORD")
        if IG_USER and IG_PASS:
            L.login(IG_USER, IG_PASS)

        profile = instaloader.Profile.from_username(L.context, username)

        fg = FeedGenerator()
        fg.title(f"Instagram feed of {username}")
        fg.link(href=f"https://www.instagram.com/{username}/", rel='alternate')
        fg.description(f"Latest public posts from {username}")

        for i, post in enumerate(profile.get_posts()):
            fe = fg.add_entry()
            fe.title(post.caption[:50] if post.caption else "Instagram Post")
            fe.link(href=post.url)
            fe.pubDate(post.date_utc)
            fe.description(post.caption or "")
            fe.enclosure(post.url, 0, "image/jpeg" if post.typename == "GraphImage" else "video/mp4")
            if i >= 4:
                break

        rssfeed = fg.rss_str(pretty=True)
        return Response(rssfeed, mimetype='application/rss+xml')

    except Exception as e:
        return f"Error: {str(e)}", 500

app.run(host='0.0.0.0', port=81)
