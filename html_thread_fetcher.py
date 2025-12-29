"""
HTML-based fetcher that follows the actual PostgreSQL archive structure:
- Monthly pages (e.g., /2025-01/) contain links to discussion threads
- Each thread page contains all messages in that thread
- We visit each thread and download all messages
"""
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime, parseaddr
from dateutil import parser as date_parser
import time

import config


class HTMLThreadFetcher:
    """Fetches emails by visiting thread pages from monthly archive pages."""
    
    def __init__(self):
        self.archive_base = "https://www.postgresql.org/list/pgsql-hackers/"
        self.current_day_archive_base = "https://www.postgresql.org/list/pgsql-hackers/since/"
        self.visited_threads: Set[str] = set()
        self.request_delay = 0.5  # Delay between requests to be respectful
    
    def fetch_weekly_messages(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch messages from HTML archive by visiting thread pages.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of message dictionaries
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        messages = []
        
        # Determine which months to check
        months_to_check = set()
        months_to_check.add((end_date.year, end_date.month, end_date.day))
        if start_date.month != end_date.month or start_date.year != end_date.year:
            months_to_check.add((start_date.year, start_date.month))
        
        print(f"   Checking months: {', '.join(f'{y}-{m:02d}-{d:02d}' for y, m, d in months_to_check)}")
        
        # Fetch threads from each month
        for year, month, day in months_to_check:
            month_messages = self._fetch_month_threads(year, month, day+1, start_date, end_date)
            #Currently adds an extra day to the thread links because it is not using centeral time and warents extra day to get the correct thread.
            messages.extend(month_messages)
            print(f"   Found {len(month_messages)} messages from {year}-{month:02d}")
        
        return messages
    
    def _fetch_month_threads(self, year: int, month: int, day: int,
                            start_date: datetime, end_date: datetime) -> List[Dict]:
        #Added day argument to make summeries daily instead of monthly.
        """Fetch all threads from a monthly archive page."""
        messages = []
        
        # Construct URL for monthly archive page
        # Format: https://www.postgresql.org/list/pgsql-hackers/YYYYMM`/
        date_str = f"{year}{month:02d}{day:02d}"
        archive_url = f"{self.current_day_archive_base}{date_str}0000/"
        
        try:
            print(f"      Fetching monthly page: {archive_url}")
            response = requests.get(archive_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all thread links
            # Thread links typically point to thread pages (not individual messages)
            thread_links = self._extract_thread_links(soup, archive_url)
            print(f"      Found {len(thread_links)} thread links")
            
            # Limit to first N threads for performance
            max_threads = config.MAX_THREADS_PER_MONTH
            if not max_threads == 'MAX':
                if len(thread_links) > max_threads:
                    print(f"      Limiting to first {max_threads} threads (out of {len(thread_links)} total)")
                    thread_links = thread_links[:max_threads]
            else:
                thread_links = thread_links
            
            # Visit each thread and download messages
            for i, thread_url in enumerate(thread_links, 1):
                if thread_url in self.visited_threads:
                    continue
                
                print(f"      [{i}/{len(thread_links)}] Fetching thread: {thread_url[:80]}...")
                thread_messages = self._fetch_thread_messages(thread_url, start_date, end_date)
                
                if thread_messages:
                    messages.extend(thread_messages)
                    print(f"         Found {len(thread_messages)} messages in thread")
                
                self.visited_threads.add(thread_url)
                
                # Be respectful with rate limiting
                time.sleep(self.request_delay)
                
        except Exception as e:
            print(f"      Error fetching month {year}-{month:02d}: {e}")
        
        return messages
    
    def _extract_thread_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links to discussion threads from monthly archive page.
        
        The monthly page gives links like: /message-id/{message-id}
        We need to convert these to flat view: /message-id/flat/{message-id}
        to get the full thread with all messages.
        """
        thread_links = []
        
        # Find all links that point to message-id (thread starters)
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            if not href:
                continue
            
            # Handle flat view links (already in correct format)
            if '/message-id/flat/' in href:
                # Already a flat view - use as-is
                if href.startswith('http'):
                    thread_url = href
                elif href.startswith('/'):
                    thread_url = f"https://www.postgresql.org{href}"
                else:
                    thread_url = urljoin(base_url, href)
                
                if thread_url not in thread_links:
                    thread_links.append(thread_url)
                continue
            
            # Look for /message-id/ links (these are thread starter messages)
            # Pattern: /message-id/{message-id} or /message-id/{message-id}#...
            else:
                # This is a thread starter link - convert to flat view
                # Original: /message-id/bgixmidc73doecg7wskq3k76g3nqnglqub7irbrwp4ppjsx43j%40fwre2x775mcl
                # Flat: /message-id/flat/bgixmidc73doecg7wskq3k76g3nqnglqub7irbrwp4ppjsx43j%40fwre2x775mcl
                
                # Extract the message-id part (everything after /message-id/)
                parts = href.split('/message-id/', 1)
                if len(parts) == 2:
                    message_id_part = parts[1]
                    # Remove any fragment (#...) from the message-id part
                    if '#' in message_id_part:
                        message_id_part = message_id_part.split('#')[0]
                    
                    # Make sure we have a valid message-id part
                    if message_id_part and message_id_part.strip():
                        # Construct flat view URL
                        flat_href = f"/message-id/flat/{message_id_part}"
                        
                        # Construct full URL
                        if href.startswith('http'):
                            # Extract base URL
                            base = '/'.join(href.split('/')[:3])  # https://www.postgresql.org
                            thread_url = f"{base}{flat_href}"
                        elif href.startswith('/'):
                            # Absolute path
                            thread_url = f"https://www.postgresql.org{flat_href}"
                        else:
                            # Relative path (unlikely but handle it)
                            thread_url = urljoin(base_url, flat_href)
                        
                        # Avoid duplicates
                        if thread_url not in thread_links:
                            thread_links.append(thread_url)
        
        return thread_links
    
    def _fetch_thread_messages(self, thread_url: str, 
                              start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch all messages from a thread page (flat view).
        
        The flat view shows all messages in a thread on one page.
        Messages are typically separated by headers or in distinct sections.
        """
        messages = []
        
        try:
            response = requests.get(thread_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # PostgreSQL flat view typically has messages separated by:
            # 1. Horizontal rules (<hr>)
            # 2. Headers with message metadata
            # 3. Div sections for each message
            
            # Strategy: Split by <hr> tags or find message sections
            message_sections = self._split_thread_by_messages(soup)
            
            if not message_sections:
                # Last resort: treat whole page as one message section
                all_text = soup.get_text().strip()
                if all_text and len(all_text) > 50:
                    message_sections = [all_text]
            
            # Extract each message
            parsed_count = 0
            for msg_section in message_sections:
                message = self._parse_message_element(msg_section, thread_url, start_date, end_date)
                if message:
                    messages.append(message)
                    parsed_count += 1
            
            if parsed_count == 0 and len(message_sections) > 0:
                # Debug: show what we tried to parse
                print(f"         DEBUG: Found {len(message_sections)} message sections but parsed 0 messages")
                if len(message_sections) > 0:
                    sample = message_sections[0]
                    if isinstance(sample, str):
                        sample_text = sample[:300]
                    elif hasattr(sample, 'get_text'):
                        sample_text = sample.get_text()[:300]
                    else:
                        sample_text = str(sample)[:300]
                    print(f"         Sample section (first 300 chars): {sample_text}")
                    # Also show what headers we're looking for
                    if isinstance(sample, str):
                        has_from = 'From:' in sample or 'from:' in sample
                        has_subject = 'Subject:' in sample or 'subject:' in sample
                        print(f"         Has 'From:': {has_from}, Has 'Subject:': {has_subject}")
            
        except Exception as e:
            print(f"         Error fetching thread {thread_url}: {e}")
        
        return messages
    
    def _split_thread_by_messages(self, soup: BeautifulSoup) -> List:
        """Split a flat view thread page into individual message sections.
        
        PostgreSQL flat view typically has messages separated by <hr> tags.
        Each message section contains headers (From, Subject, Date, etc.) and body.
        We use text-based splitting which is more reliable than HTML parsing.
        """
        message_sections = []
        
        # Get all text from the page
        all_text = soup.get_text()
        
        if not all_text or len(all_text.strip()) < 50:
            return []
        
        # Method 1: Split by "From:" headers (most reliable - each message starts with "From:")
        # Pattern: "From:" at start of line (possibly with leading whitespace/newline)
        from_pattern = re.compile(r'(?:^|\n)From:\s+', re.IGNORECASE | re.MULTILINE)
        matches = list(from_pattern.finditer(all_text))
        
        if len(matches) > 0:
            # Found message boundaries
            for i in range(len(matches)):
                start_pos = matches[i].start()
                # Skip the newline if present
                if all_text[start_pos] == '\n':
                    start_pos += 1
                
                end_pos = matches[i+1].start() if i+1 < len(matches) else len(all_text)
                message_text = all_text[start_pos:end_pos].strip()
                
                if message_text and len(message_text) > 50:  # Valid message (at least 50 chars)
                    message_sections.append(message_text)
        
        # Method 2: If no "From:" patterns, try splitting by <hr> tags in HTML
        if not message_sections:
            html_str = str(soup)
            # Split by <hr> or <hr/> tags
            parts = re.split(r'<hr[^>]*>', html_str, flags=re.IGNORECASE)
            
            for part in parts:
                if part.strip():
                    part_soup = BeautifulSoup(part, 'html.parser')
                    text = part_soup.get_text().strip()
                    if text and len(text) > 50:
                        message_sections.append(text)
        
        # Method 3: Last resort - treat whole page as single message
        if not message_sections:
            text = all_text.strip()
            if text and len(text) > 50:
                message_sections.append(text)
        
        return message_sections
    
    
    def _parse_message_element(self, msg_elem, thread_url: str,
                              start_date: datetime, end_date: datetime) -> Dict:
        """Parse a message element into a message dictionary.
        
        msg_elem can be:
        - A string (text content)
        - A BeautifulSoup element
        """
        try:
            # Get text content for parsing
            if isinstance(msg_elem, str):
                text = msg_elem
            elif hasattr(msg_elem, 'get_text'):
                text = msg_elem.get_text()
            else:
                text = str(msg_elem)
            
            # Ensure we have valid text
            if not text or len(text.strip()) < 20:
                return None
            
            # Extract headers using regex patterns (more reliable for flat view)
            from_header = self._extract_header_from_text(text, 'From')
            subject = self._extract_header_from_text(text, 'Subject')
            date_header = self._extract_header_from_text(text, 'Date')
            message_id = self._extract_header_from_text(text, 'Message-ID')
            in_reply_to = self._extract_header_from_text(text, 'In-Reply-To')
            references = self._extract_header_from_text(text, 'References')
            to_header = self._extract_header_from_text(text, 'To')
            
            # Extract body (everything after headers)
            body = self._extract_message_body_from_text(text)
            
            # Parse date - be lenient, use fallback if parsing fails
            msg_date = None
            if date_header:
                try:
                    msg_date = parsedate_to_datetime(date_header)
                except Exception:
                    # Try to extract date from text if standard parsing fails
                    # Look for common date patterns
                    date_patterns = [
                        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                        r'(\w{3},?\s+\d{1,2}\s+\w{3}\s+\d{4})',  # Mon, DD MMM YYYY
                    ]
                    for pattern in date_patterns:
                        match = re.search(pattern, date_header)
                        if match:
                            try:
                                msg_date = date_parser.parse(match.group(1))
                                break
                            except Exception:
                                pass
            
            # If still no date, use a date in the middle of the range as fallback
            if not msg_date:
                msg_date = start_date + (end_date - start_date) / 2
            
            # Check if we have at least a subject or from header (basic validation)
            if not subject and not from_header:
                # Not a valid message
                return None
            
            # Check if message is in date range (with some tolerance for parsing errors)
            # If date is close to range, include it
            if not (start_date - timedelta(days=1) <= msg_date <= end_date + timedelta(days=1)):
                return None
            
            # Parse sender
            sender_name, sender_email = parseaddr(from_header) if from_header else ('', '')
            
            # Generate message ID if not found
            if not message_id:
                # Try to extract from thread URL or generate one
                if '/message-id/' in thread_url:
                    # Use thread URL as base for message ID
                    message_id = f"{thread_url}#{hash(subject + str(msg_date))}"
                else:
                    message_id = f"msg-{hash(text)}"
            
            return {
                'message_id': message_id,
                'subject': subject or 'No Subject',
                'sender_name': sender_name,
                'sender_email': sender_email,
                'from_addr': from_header or '',
                'to_addr': to_header or '',
                'date': msg_date,
                'in_reply_to': in_reply_to or '',
                'references': references or '',
                'body': body,
                'raw_message': None
            }
            
        except Exception as e:
            print(f"         Error parsing message element: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_header_from_text(self, text: str, header_name: str) -> str:
        """Extract email header value from text using regex."""
        # Pattern: "Header: value" - can be at start of line or after whitespace
        # Handle both "From: name@email.com" and "From: name <email@domain.com>"
        pattern = re.compile(
            rf'^{re.escape(header_name)}\s*:\s*(.+?)(?:\n|$)',
            re.IGNORECASE | re.MULTILINE
        )
        match = pattern.search(text)
        if match:
            value = match.group(1).strip()
            # Remove any trailing content that looks like next header
            # Stop at next header pattern (word followed by colon at start of line)
            value = re.split(r'\n(?=\w+\s*:)', value)[0].strip()
            # Clean up any remaining newlines or extra whitespace
            value = ' '.join(value.split())
            return value
        return ''
    
    def _extract_message_body_from_text(self, text: str) -> str:
        """Extract message body from text (everything after headers)."""
        # Find where headers end and body begins
        # Headers typically end with a blank line or before quoted content
        
        # Split by common header patterns
        lines = text.split('\n')
        body_start = 0
        
        # Find the last header
        header_pattern = re.compile(r'^\w+\s*:')
        for i, line in enumerate(lines):
            if header_pattern.match(line.strip()):
                body_start = i + 1
            elif line.strip() == '' and body_start > 0:
                # Blank line after headers - body starts here
                body_start = i + 1
                break
        
        # Extract body
        body_lines = lines[body_start:]
        
        # Remove common quote markers
        cleaned_lines = []
        for line in body_lines:
            # Remove leading ">" quote markers
            line = re.sub(r'^>\s*', '', line)
            cleaned_lines.append(line)
        
        body = '\n'.join(cleaned_lines).strip()
        
        # Remove signature patterns (common email signatures)
        body = re.split(r'\n--\s*\n', body)[0]  # Stop at signature separator
        
        return body
    


