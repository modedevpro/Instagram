from flask import Flask, request, jsonify
import instaloader
import contextlib

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "status": "running",
        "usage": "/download?url=INSTAGRAM_URL"
    }

@app.route("/download")
def download():

    data = {}

    try:
        url = request.args.get("url")

        if not url:
            return jsonify({"error": "ضع رابط انستقرام"}), 400

        url = url.split("?")[0]

        L = instaloader.Instaloader()

        # ---------------- POSTS / REELS ----------------
        if "/reel/" in url or "/p/" in url:

            shortcode = url.split("/")[-2]

            with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                post = instaloader.Post.from_shortcode(L.context, shortcode)

            data["type"] = "post"
            data["shortcode"] = shortcode
            data["media_id"] = f"{post.mediaid}_{post.owner_id}"
            data["username"] = post.owner_username
            data["owner_id"] = post.owner_id
            data["caption"] = post.caption
            data["likes"] = post.likes
            data["comments"] = post.comments
            data["video_duration"] = post.video_duration

            media = []

            if post.typename == "GraphSidecar":

                for node in post.get_sidecar_nodes():

                    if node.is_video:
                        media.append({
                            "type": "video",
                            "url": node.video_url
                        })
                    else:
                        media.append({
                            "type": "image",
                            "url": node.display_url
                        })

            else:

                if post.is_video:
                    media.append({
                        "type": "video",
                        "url": post.video_url
                    })
                else:
                    media.append({
                        "type": "image",
                        "url": post.url
                    })

            data["media"] = media

        # ---------------- STORIES ----------------
        elif "/stories/" in url:

            username = url.split("/stories/")[1].split("/")[0]

            with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                profile = instaloader.Profile.from_username(L.context, username)

            data["type"] = "story"
            data["username"] = username
            data["owner_id"] = profile.userid

            media = []

            for story in L.get_stories(userids=[profile.userid]):

                for item in story.get_items():

                    if item.is_video:
                        media.append({
                            "type": "video",
                            "url": item.video_url
                        })
                    else:
                        media.append({
                            "type": "image",
                            "url": item.url
                        })

                    break
                break

            data["media"] = media

        else:
            data["error"] = "الرابط غير مدعوم"

    except Exception as e:
        data["error"] = str(e)

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
