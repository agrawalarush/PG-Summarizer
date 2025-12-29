"""
Configuration settings for the pgsql-hackers blog generator.
"""
from ast import Num
import os
from datetime import datetime, timedelta

# Mailing list archive URLs
PG_HACKERS_ARCHIVE_BASE = "https://www.postgresql.org/message-id/"
PG_HACKERS_MBOX_BASE = "https://www.postgresql.org/list/pgsql-hackers/"

# Output directory for generated blogs
BLOG_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "blogs")

# PostgreSQL committers list (will be fetched/updated)
COMMITTERS_FILE = os.path.join(os.path.dirname(__file__), "committers.txt")

# Number of top threads to select
TOP_THREADS_COUNT = 'MAX'
#Max Allows all threads of that day to be summarized.
#Else specify the number of threads to summarize.

NUMBER_OF_TOP_THREADS_TO_SUMMARIZE = 5
#Number of threads to summarize.

# Date range for weekly analysis (days back from today)
WEEKLY_DAYS_BACK = 7

# Maximum number of threads to fetch per month (for performance)
MAX_THREADS_PER_MONTH = TOP_THREADS_COUNT
#this is the same thing twice

# Blog post template settings
BLOG_TEMPLATE = "blog_template.md"
BLOG_DATE_FORMAT = "%Y-%m-%d"

# Activity scoring weights
WEIGHT_MESSAGE_COUNT = 1.0
WEIGHT_COMMITTER_COUNT = 2.0
WEIGHT_UNIQUE_PARTICIPANTS = 0.5



