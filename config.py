"""
Configuration settings for the pgsql-hackers blog generator.
"""

import os
from datetime import timedelta

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)

BLOG_OUTPUT_DIR = os.path.join(BASE_DIR, "blogs")
COMMITTERS_FILE = os.path.join(BASE_DIR, "committers.txt")

# -------------------------------------------------------------------
# PostgreSQL mailing list archives
# -------------------------------------------------------------------

PG_HACKERS_ARCHIVE_BASE = "https://www.postgresql.org/list/pgsql-hackers/"

# -------------------------------------------------------------------
# Thread selection & limits
# -------------------------------------------------------------------

# Number of top threads to summarize per run
NUM_SUMMARY_THREADS = 3

# Days back from today for weekly analysis
WEEKLY_DAYS_BACK = 7

# Max threads fetched per month (None = no limit)
MAX_THREADS = None

# -------------------------------------------------------------------
# Blog formatting
# -------------------------------------------------------------------

BLOG_TEMPLATE = "blog_template.md"
BLOG_DATE_FORMAT = "%Y-%m-%d"

# -------------------------------------------------------------------
# Activity scoring weights
# -------------------------------------------------------------------

WEIGHT_MESSAGE_COUNT = 1.0
WEIGHT_COMMITTER_COUNT = 2.0
WEIGHT_UNIQUE_PARTICIPANTS = 0.5

# -------------------------------------------------------------------
# OpenAI configuration
# -------------------------------------------------------------------
# IMPORTANT:
# Set your API key as an environment variable:
# export OPENAI_API_KEY="sk-..."

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -------------------------------------------------------------------
# PostgreSQL committers
# -------------------------------------------------------------------

COMMITTERS = [
    "Bruce Momjian",
    "Tom Lane",
    "Tatsuo Ishii",
    "Peter Eisentraut",
    "Joe Conway",
    "Álvaro Herrera",
    "Andrew Dunstan",
    "Magnus Hagander",
    "Heikki Linnakangas",
    "Robert Haas",
    "Jeff Davis",
    "Fujii Masao",
    "Noah Misch",
    "Andres Freund",
    "Dean Rasheed",
    "Alexander Korotkov",
    "Amit Kapila",
    "Tomas Vondra",
    "Michael Paquier",
    "Thomas Munro",
    "Peter Geoghegan",
    "Etsuro Fujita",
    "David Rowley",
    "Daniel Gustafsson",
    "John Naylor",
    "Nathan Bossart",
    "Amit Langote",
    "Masahiko Sawada",
    "Melanie Plageman",
    "Richard Guo",
    "Jacob Champion",
]
