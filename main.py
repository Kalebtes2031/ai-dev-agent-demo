"""Entry point placeholder for ai_dev_agent."""

import os
from dotenv import load_dotenv
from bot.bot import run_bot

# Load environment variables from .env
load_dotenv()

def main() -> None:
    print("Starting GitHub Assistance bot...")
    run_bot()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye")
