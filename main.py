import json
import os
import re
import logging
from send2trash import send2trash

# local imports
from notion import save_notion_page
import oai

logging.basicConfig(level=logging.INFO)


def file_exists(folder_path, file_to_match):
    for filename in os.listdir(folder_path):
        if filename == file_to_match:
            return True
    return False


def file_to_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def process_tweets(content):
    try:
        tweets = content["data"]
        users = {}
        for user in content["includes"]["users"]:
            key = user["id"]
            users[key] = user

        medias = {}
        for media in content["includes"]["media"]:
            key = media["media_key"]
            medias[key] = media

        for tweet in tweets:
            # author info
            author_id = tweet["author_id"]
            username = users[author_id]["username"]
            author_name = "@" + users[author_id]["name"]

            # tweet info
            post_id = tweet["id"]
            post_url = f"https://twitter.com/{username}/status/{post_id}"

            # tweet content
            tweet_text = (
                tweet["note_tweet"]["text"] if "note_tweet" in tweet else tweet["text"]
            )
            pic_url_regex = r"(https:\/\/t\.co\/[\w\d]+)"
            split_text = re.split(pic_url_regex, tweet_text)

            # Generate post title with OpenAI
            prompt = f"Please create a concise, 3-5 word phrase as a header for the following, strictly adhering to the 3-5 word limit: {tweet_text}"
            openai = oai.Openai()
            post_title = openai.complete(prompt=prompt).strip().replace('"', "")

            # tweet attachments
            picture_urls = []
            video_urls = []
            if "attachments" in tweet:
                keys = tweet["attachments"]["media_keys"]
                for key in keys:
                    if medias[key]["type"] == "photo":
                        picture_urls.append(medias[key]["url"])
                    if (
                        medias[key]["type"] == "video"
                        or medias[key]["type"] == "animated_gif"
                    ):
                        logging.info(f"Video found: {medias[key]} ")
                        preview_url = medias[key]["preview_image_url"]
                        video = sorted(
                            medias[key]["variants"],
                            key=lambda x: x["bit_rate"] if "bit_rate" in x else 0,
                        )
                        video_urls.append(
                            {
                                "preview_url": preview_url,
                                "video_url": video[-1]["url"],
                            }
                        )

            save_notion_page(
                post_id,
                post_url,
                author_name,
                post_title,
                picture_urls,
                video_urls,
                split_text,
            )

    except json.decoder.JSONDecodeError:
        return None

    return len(tweets)


if __name__ == "__main__":
    file = "bookmarked_twitters.txt"
    folder = os.path.join(os.getcwd(), "../../../Downloads/TwitterNotion")
    if not file_exists(folder, file):
        logging.error(f"File {file} not found in {folder}")
        exit(1)

    file_content = file_to_json(os.path.join(folder, file))
    synced_count = process_tweets(file_content)
    if synced_count:
        logging.info(f"Synced {synced_count} tweets successfully🎉")
        # delete the file after syncing
        try:
            send2trash(os.path.join(folder, file))
            logging.info(f"Deleted {file} from {folder}")
        except OSError as e:
            logging.error(e)
