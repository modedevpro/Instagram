from flask import Flask, request, Response
import instaloader
import contextlib
import json
import time

app = Flask(__name__)

@app.route("/")
def home():
    data = {
        "status": "running",
        "usage": [
            "/download?url=INSTAGRAM_URL",
            "/download?user=USERNAME"
        ]
    }
    return Response(json.dumps(data, ensure_ascii=False), mimetype="application/json")


@app.route("/download")
def download():

    data = {}

    try:

        url = request.args.get("url")
        username_param = request.args.get("user")

        L = instaloader.Instaloader()

        # تسجيل الدخول
        with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
            L.login("modesadelsa", "123###***qweQWE")

        # ---------------- POST / REEL ----------------
        if url and ("/reel/" in url or "/p/" in url):

            url = url.split("?")[0]
            shortcode = url.split("/")[-2]

            # retry لتجنب rate limit
            for i in range(3):
                try:
                    with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                        post = instaloader.Post.from_shortcode(L.context, shortcode)
                    break
                except:
                    time.sleep(3)

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


        # ---------------- STORY FROM LINK ----------------
        elif url and "/stories/" in url:

            url = url.split("?")[0]
            username = url.split("/stories/")[1].split("/")[0]

            with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                profile = instaloader.Profile.from_username(L.context, username)

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

            data["type"] = "story"
            data["username"] = username
            data["owner_id"] = profile.userid
            data["media"] = media


        # ---------------- STORY FROM USERNAME ----------------
        elif username_param:

            username = username_param

            with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                profile = instaloader.Profile.from_username(L.context, username)

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

            data["type"] = "story"
            data["username"] = username
            data["owner_id"] = profile.userid
            data["media"] = media


        else:
            data["error"] = "الرابط أو اسم المستخدم غير مدعوم"

    except Exception as e:
        data["error"] = str(e)

    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype="application/json"
    )


app = app
