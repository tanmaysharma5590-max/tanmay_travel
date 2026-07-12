from tavily import TavilyClient
import os
import time
import requests
from dotenv import load_dotenv

# override=True ensures values from the .env file always take priority
# over any stale environment variable that might already be set on the system
load_dotenv(override=True)


# https://www.tavily.com/
# Signup and login, On dashboard- > under api keys you will see the default key.
# Use that or click on + to create new one. Then save it in .env file

_api_key = os.getenv("TAVILY_API_KEY")

if not _api_key:
    raise ValueError(
        "TAVILY_API_KEY not found. Make sure it is set in your .env file "
        "in the project root (same folder as main.py)."
    )

client = TavilyClient(api_key=_api_key)


def tavily_search(query, max_retries=3, retry_delay=2):
    """
    Searches Tavily with automatic retries on connection errors.
    If all retries fail, returns a graceful fallback message instead of crashing.
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.search(
                query=query,
                max_results=5
            )

            results = []
            for i, r in enumerate(response["results"], 1):
                title   = r.get("title", "Unknown")
                url     = r.get("url", "")
                snippet = r.get("content", "").strip()
                if len(snippet) > 300:
                    snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

                results.append(f"{i}. **{title}**\n   {url}\n   {snippet}")

            return "\n\n".join(results)

        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException) as e:
            last_error = e
            print(f"[tavily_search] Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(retry_delay)
                retry_delay *= 2
            continue

        except Exception as e:
            # Non-network errors (e.g. invalid API key) - don't retry, fail fast
            last_error = e
            break

    print(f"[tavily_search] Failed after {max_retries} attempts: {last_error}")
    return (
        "_Could not fetch search results right now due to a network issue. "
        "Please check your internet connection and try again._"
    )