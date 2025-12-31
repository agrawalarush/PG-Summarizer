#!/usr/bin/env python3
"""
Main script to generate weekly blog posts from pgsql-hackers mailing list
using fetch_urls.py, parse_threads.py, ThreadSelector, and BlogGenerator.
"""

import sys
from datetime import datetime, timedelta

from html_thread_fetcher import HTMLThreadFetcher
from blog_generator import BlogGenerator
from thread_analyzer import HTMLThreadParser
from thread_selector import ThreadSelector
import config


def main():
    """Main function to generate weekly blog post."""
    print("=" * 60)
    print("PostgreSQL Hackers Weekly Blog Generator")
    print("=" * 60)
    print()

    # 1. Initialize blog generator
    print("1. Initializing BlogGenerator...")
    blog_generator = BlogGenerator()
    thread_fetcher = HTMLThreadFetcher()
    thread_parser = HTMLThreadParser()
    
    print()

    # 2. Fetch threads from the last N days
    print(f"2. Fetching threads from the last {config.WEEKLY_DAYS_BACK} days...")
    try:
        thread_urls = thread_fetcher.get_today_thread_urls()
        print(f"   - Found {len(thread_urls)} threads")
    except Exception as e:
        print(f"   ERROR: Failed to fetch thread URLs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not thread_urls:
        print("   ERROR: No threads found for the specified period.")
        sys.exit(1)
    print()

    # 3. Fetch and parse messages for all threads
    print("3. Fetching and parsing thread messages...")
    try:
        all_threads = thread_parser.fetch_threads(thread_urls)
        print(f"   - Fetched and parsed {len(all_threads)} threads")
    except Exception as e:
        print(f"   ERROR: Failed to fetch/parse threads: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not all_threads:
        print("   ERROR: No messages parsed from threads.")
        sys.exit(1)
    print()

    # 4. Select top threads
    print(f"4. Selecting top {config.NUM_SUMMARY_THREADS} threads...")
    try:
        selector = ThreadSelector(top_count=config.NUM_SUMMARY_THREADS)
        top_threads = selector.select_top_threads(all_threads)
        print(f"   - Selected {len(top_threads)} top threads")
    except Exception as e:
        print(f"   ERROR: Failed to select top threads: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not top_threads:
        print("   ERROR: No threads selected after ranking.")
        sys.exit(1)
    print()

    # 5. Generate blog post from selected threads
    print("5. Generating blog post from selected threads...")
    try:
        for thread in top_threads:
            # For simplicity, generate summary from first message body
            blog_generator.generate_summary(html_content=thread['messages'][0]['body'])
    except Exception as e:
        print(f"   ERROR: Failed to generate blog post: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 60)
    print("SUCCESS: Weekly blog post generated!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
