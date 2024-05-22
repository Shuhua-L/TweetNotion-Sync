# TweetNotion-Sync

## About
TweetNotion-Sync is a tool designed to save bookmarked or liked tweets to a Notion database. It utilizes OpenAI to generate titles based on the tweet content.

## Features
- Sync bookmarked or liked tweets to a specified Notion database.
- Generate titles for tweets using OpenAI.
- Automate the process with environment variables for configuration.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/Shuhua-L/TweetNotion-Sync.git
    ```
2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
1. Copy `.env_template` to `.env` and fill in your credentials:
    ```bash
    cp .env_template .env
    ```
2. Update the `.env` file with your Notion API credentials and OpenAI credentials.

## Usage
Run the main script:
```bash
python main.py
```

## Prerequisites
- Notion API credentials
- OpenAI credentials
