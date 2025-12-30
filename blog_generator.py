"""
Module to generate blog posts from thread summaries.
"""
import os
from datetime import datetime
from typing import List, Dict
from jinja2 import Template

import config


class BlogGenerator:
    """Generates blog posts from thread summaries."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or config.BLOG_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_weekly_blog(self, summaries: List[Dict], week_start: datetime = None) -> str:
        """
        Generate a weekly blog post from thread summaries.
        
        Args:
            summaries: List of thread summary dictionaries
            week_start: Start date of the week (defaults to today)
            
        Returns:
            Path to generated blog file
        """
        if week_start is None:
            week_start = datetime.now()
        
        week_end = week_start
        
        # Generate blog content
        blog_content = self._create_blog_content(summaries, week_start, week_end)
        
        # Generate filename
        date_str = week_start.strftime(config.BLOG_DATE_FORMAT)
        filename = f"pgsql-hackers-weekly-{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Write blog file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(blog_content)
        
        print(f"Generated blog post: {filepath}")
        return filepath
    
    def _create_blog_content(self, summaries: List[Dict], week_start: datetime, week_end: datetime) -> str:
        """Create blog post content from summaries."""
        
        # Blog template
        template_str = """# PostgreSQL Hackers Weekly Summary

**Week of {{ week_start.strftime('%B %d, %Y') }}**

This weekly summary highlights the top {{ thread_count }} most active discussions from the [pgsql-hackers](https://www.postgresql.org/list/pgsql-hackers/) mailing list, focusing on design discussions, implementation progress, and contributions from PostgreSQL committers.

---

{% for summary in summaries %}
## {{ loop.index }}. {{ summary.subject }}

**Thread Activity:**
- **Messages:** {{ summary.message_count }}
- **Participants:** {{ summary.participants|length }}
- **PostgreSQL Committers:** {{ summary.committers|length }}
{% if summary.committers %}
- **Committers Involved:** {{ summary.committers|join(', ') }}
{% endif %}
- **Thread Duration:** {{ summary.start_date.strftime('%Y-%m-%d') }} to {{ summary.end_date.strftime('%Y-%m-%d') }}

### Summary

{{ summary.summary_text }}

{% if summary.discussion_points %}
### Key Discussion Points

{% for point in summary.discussion_points[:5] %}
- {{ point }}
{% endfor %}
{% endif %}

{% if summary.design_decisions %}
### Design Decisions

{% for decision in summary.design_decisions[:5] %}
- {{ decision }}
{% endfor %}
{% endif %}

{% if summary.progress_items %}
### Progress Updates

{% for progress in summary.progress_items[:5] %}
- {{ progress }}
{% endfor %}
{% endif %}

{% if summary.action_items %}
### Action Items

{% for action in summary.action_items[:5] %}
- {{ action }}
{% endfor %}
{% endif %}

---

{% endfor %}

## About This Summary

This summary is automatically generated weekly from the pgsql-hackers mailing list archive. Threads are selected based on:
- Maximum activity (message count and participant engagement)
- Involvement of PostgreSQL committers
- Design and implementation discussions

For the full discussions, please visit the [pgsql-hackers mailing list archive](https://www.postgresql.org/list/pgsql-hackers/).

---
*Generated on {{ generation_date.strftime('%Y-%m-%d %H:%M:%S') }}*
"""
        
        template = Template(template_str)
        
        content = template.render(
            summaries=summaries,
            week_start=week_start,
            week_end=week_end,
            thread_count=len(summaries),
            generation_date=datetime.now()
        )
        
        return content



