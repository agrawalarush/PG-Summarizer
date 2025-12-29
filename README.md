# PostgreSQL Hackers Weekly Blog Generator

Automatically generates weekly blog posts summarizing the top 5 most active discussions from the pgsql-hackers mailing list, with a focus on design discussions and PostgreSQL committer involvement.

## Features

- **Direct Archive Access**: Pulls data directly from the PostgreSQL mailing list archive (no intermediate database)
- **Automatic Thread Analysis**: Groups emails into threads and calculates activity metrics
- **Committer Detection**: Identifies and prioritizes threads with PostgreSQL committer participation
- **Intelligent Selection**: Selects top 5 threads based on:
  - Maximum activity (message count, participant engagement)
  - PostgreSQL committer involvement
  - Recent activity
- **Detailed Summaries**: Generates comprehensive summaries including:
  - Key discussion points
  - Design decisions
  - Progress updates
  - Action items
- **Weekly Automation**: Designed to run weekly via cron job

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Make the main script executable:**
   ```bash
   chmod +x main.py
   ```

## Usage

### Manual Execution

Run the script manually to generate a blog post for the current week:

```bash
python main.py
```

The script will:
1. Fetch emails from the last 7 days
2. Analyze and group messages into threads
3. Calculate activity metrics and identify committer involvement
4. Select the top 5 threads
5. Generate detailed summaries
6. Create a blog post in the `blogs/` directory

### Weekly Automation

To run automatically every week, add a cron job:

```bash
# Edit crontab
crontab -e

# Add this line to run every Monday at 9 AM
0 9 * * 1 cd /home/sayona/ArushCode/pg && /usr/bin/python3 main.py
```

Or create a systemd timer for more control (see `pgsql-blog-weekly.timer` and `pgsql-blog-weekly.service` files).

## Configuration

Edit `config.py` to customize:

- `WEEKLY_DAYS_BACK`: Number of days to look back (default: 7)
- `TOP_THREADS_COUNT`: Number of top threads to select (default: 5)
- `BLOG_OUTPUT_DIR`: Directory for generated blog posts
- Activity scoring weights for thread selection

## Project Structure

```
pg/
├── main.py                 # Main script
├── config.py               # Configuration settings
├── email_fetcher.py        # Fetches emails from archive
├── committer_detector.py   # Detects PostgreSQL committers
├── thread_analyzer.py      # Analyzes threads and calculates metrics
├── thread_selector.py      # Selects top threads
├── thread_summarizer.py    # Generates thread summaries
├── blog_generator.py       # Generates blog posts
├── requirements.txt        # Python dependencies
├── committers.txt          # Cached committer list (auto-generated)
└── blogs/                  # Generated blog posts directory
```

## How It Works

1. **Email Fetching**: Downloads mbox files from the PostgreSQL mailing list archive for the relevant time period. If mbox files are not directly accessible, an alternative HTML parser is available (`archive_fetcher_alternative.py`).
2. **Thread Grouping**: Groups messages into threads using Subject headers and References/In-Reply-To fields
3. **Activity Calculation**: Calculates activity scores based on:
   - Message count
   - Number of unique participants
   - Committer involvement (weighted higher)
4. **Thread Selection**: Prioritizes threads with:
   - Committer participation
   - High activity scores
   - Recent activity
5. **Summarization**: Extracts key information including:
   - Discussion points
   - Design decisions
   - Progress updates
   - Action items
6. **Blog Generation**: Creates a formatted markdown blog post with all summaries

## Alternative Email Fetching

If the mbox files are not directly accessible from the archive, you can use the HTML-based fetcher by modifying `main.py`:

```python
# In main.py, change:
from email_fetcher import EmailFetcher
# To:
from archive_fetcher_alternative import HTMLArchiveFetcher as EmailFetcher
```

The HTML fetcher parses archive pages directly, which may be slower but more reliable if mbox access is restricted.

## Output

Blog posts are generated as Markdown files in the `blogs/` directory with the format:
```
pgsql-hackers-weekly-YYYY-MM-DD.md
```

Each blog post includes:
- Overview of the week's top discussions
- Detailed summaries for each of the top 5 threads
- Key discussion points, design decisions, and progress updates
- Thread statistics (message count, participants, committer involvement)

## Notes

- The committer list is automatically fetched and cached in `committers.txt`
- The script pulls data directly from the archive each week (no database)
- Thread grouping uses heuristics based on email headers; some edge cases may occur
- Summarization uses pattern matching; for production use, consider integrating NLP libraries

## Troubleshooting

**No messages found:**
- Check your internet connection
- Verify the archive URLs in `config.py` are correct
- The time period may not have had sufficient activity

**Thread grouping issues:**
- Some threads may be split if email headers are inconsistent
- This is a known limitation of header-based thread reconstruction

**Committer detection:**
- The committer list is cached; run `committer_detector.update_committers()` to refresh
- Some committers may use different email addresses

## License

This project is provided as-is for generating weekly summaries of PostgreSQL development discussions.

