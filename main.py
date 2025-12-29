#!/usr/bin/env python3
"""
Main script to generate weekly blog posts from pgsql-hackers mailing list.
"""
import os
import sys
from datetime import datetime, timedelta

from committer_detector import CommitterDetector
from thread_analyzer import ThreadAnalyzer
from thread_selector import ThreadSelector
from thread_summarizer import ThreadSummarizer
from blog_generator import BlogGenerator

import config

from html_thread_fetcher import HTMLThreadFetcher


def main():
    """Main function to generate weekly blog post."""
    print("=" * 60)
    print("PostgreSQL Hackers Weekly Blog Generator")
    print("=" * 60)
    print()
    
    # Initialize components
    print("1. Initializing components...")
    committer_detector = CommitterDetector()
    thread_analyzer = ThreadAnalyzer(committer_detector.get_committers())
    thread_selector = ThreadSelector(top_count=config.TOP_THREADS_COUNT)
    thread_summarizer = ThreadSummarizer()
    blog_generator = BlogGenerator()
    
    print(f"   - Loaded {len(committer_detector.get_committers())} PostgreSQL committers")
    print()
    
    # Fetch emails from the last week
    print(f"2. Fetching emails from the last {config.WEEKLY_DAYS_BACK} days...")
    try:
        html_thread_fetcher = HTMLThreadFetcher()
        messages = html_thread_fetcher.fetch_weekly_messages(days_back=config.WEEKLY_DAYS_BACK)
        print(f"   - Fetched {len(messages)} messages")
    except Exception as e:
        print(f"   ERROR: Failed to fetch messages: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if not messages:
        print("   ERROR: No messages found for the specified period.")
        print("   Possible reasons:")
        print("   - Archive URLs may have changed")
        print("   - Network connectivity issues")
        print("   - No activity in the specified time period")
        print("   - Archive format may require different access method")
        print()
        print("   Consider:")
        print("   - Checking archive manually: https://www.postgresql.org/list/pgsql-hackers/")
        print("   - Verifying the date range")
        print("   - Using a different fetcher method")
        sys.exit(1)
    
    print()
    
    # Analyze threads
    print("3. Analyzing email threads...")
    try:
        analyzed_threads = thread_analyzer.analyze_all_threads(messages)
        print(f"   - Found {len(analyzed_threads)} unique threads")
    except Exception as e:
        print(f"   ERROR: Failed to analyze threads: {e}")
        sys.exit(1)
    
    print()
    
    # Select top threads
    print(f"4. Selecting top {config.TOP_THREADS_COUNT} threads...")
    try:
        top_threads = thread_selector.select_top_threads(analyzed_threads)
        print(f"   - Selected {len(top_threads)} top threads")
        
        for i, thread in enumerate(top_threads, 1):
            committer_info = f" ({thread['committer_count']} committers)" if thread.get('committer_count', 0) > 0 else ""
            print(f"   {i}. {thread['subject'][:60]}... - {thread['message_count']} messages{committer_info}")
    except Exception as e:
        print(f"   ERROR: Failed to select threads: {e}")
        sys.exit(1)
    
    print()
    
    # Generate summaries
    print("5. Generating thread summaries...")
    try:
        summaries = []
        for thread in top_threads:
            summary = thread_summarizer.summarize_thread(thread)
            if summary:
                summaries.append(summary)
        print(f"   - Generated {len(summaries)} summaries")
    except Exception as e:
        print(f"   ERROR: Failed to generate summaries: {e}")
        sys.exit(1)
    
    print()
    
    # Generate blog post
    print("6. Generating blog post...")
    try:
        week_start = datetime.now() - timedelta(days=config.WEEKLY_DAYS_BACK)
        blog_path = blog_generator.generate_weekly_blog(summaries, week_start)
        print(f"   - Blog post generated: {blog_path}")
    except Exception as e:
        print(f"   ERROR: Failed to generate blog post: {e}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("SUCCESS: Weekly blog post generated!")
    print("=" * 60)
    print(f"Output: {blog_path}")
    print()


if __name__ == "__main__":
    main()


