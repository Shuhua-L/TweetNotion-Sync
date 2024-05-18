import logging
import os
from notion_client import Client

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    logging.error("Could not load .env because python-dotenv not found.")
else:
    load_dotenv()


NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
DATABASE_ID = os.getenv("DATABASE_ID", "")


# Initialize the client
notion = Client(auth=NOTION_TOKEN)

# Make sure the database is connected
print("\nSearching for connected databases... ")
results = notion.search(filter={"value": "database", "property": "object"}).get(
    "results"
)
if results:
    print("Databases connected:", results[0]["id"])


def save_notion_page(
    post_id,
    post_url,
    author_name,
    tweet_text,
    post_title,
    picture_urls,
    video_urls,
):
    properties = {
        "Title": {"title": [{"text": {"content": post_title}}]},
        "Link": {"url": post_url},
        "Author": {
            "rich_text": [{"text": {"content": author_name}}],
        },
        "ID": {"number": int(post_id)},
    }

    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": tweet_text,
                        },
                    }
                ],
                "color": "purple_background",
            },
        }
    ]

    for url in picture_urls:
        children.append(
            {
                "type": "image",
                "image": {"type": "external", "external": {"url": url}},
            }
        )

    for video in video_urls:
        children.append(
            {
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {"url": video["preview_url"]},
                },
            }
        )
        children.append(
            {
                "type": "bookmark",
                "bookmark": {
                    "caption": [],
                    "url": video["video_url"],
                },
            }
        )

    page_block = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties,
        "children": children,
    }

    try:
        notion.pages.create(**page_block)
        logging.info(f"Saved {post_id} to Notion 🎉")
    except Exception as e:
        logging.error(e)
