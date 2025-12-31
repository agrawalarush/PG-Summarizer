import re
import requests
from bs4 import BeautifulSoup
from email.utils import parseaddr

class HTMLThreadParser:
    """Fetches email messages from PostgreSQL mailing list flat thread URLs."""

    def __init__(self):
        self.request_delay = 0.5  # seconds

    def fetch_threads(self, thread_urls: list):
        """Fetch multiple thread URLs and return structured output by thread."""
        all_threads = []

        for url in thread_urls:
            messages = self.fetch_thread_messages(url)
            if messages:
                thread_name = messages[0]["subject"] if messages else "No Subject"
                all_threads.append({
                    "Thread_name": thread_name,
                    "messages": [
                        {"subject": m["subject"], "sender_name": m["sender_name"], "body": m["body"], "date": m["date"]}
                        for m in messages
                    ]
                })

        return all_threads

    def fetch_thread_messages(self, thread_url: str):
        """Fetch all messages from a single flat-view thread URL."""
        response = requests.get(thread_url, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")

        messages = []
        message_sections = self._split_thread_by_messages(soup)

        for msg_section in message_sections:
            msg = self._parse_message_element(msg_section)
            if msg:
                messages.append(msg)

        return messages

    def _split_thread_by_messages(self, soup):
        all_text = soup.get_text()
        message_sections = []
        from_pattern = re.compile(r"(?:^|\n)From:\s+", re.IGNORECASE | re.MULTILINE)
        matches = list(from_pattern.finditer(all_text))
        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(all_text)
            text = all_text[start_pos:end_pos].strip()
            if len(text) > 50:
                message_sections.append(text)
        return message_sections or [all_text]

    def _parse_message_element(self, msg_elem):
        text = str(msg_elem)
        from_header = self._extract_header_from_text(text, "From")
        subject = self._extract_header_from_text(text, "Subject") or "No Subject"
        body = self._extract_message_body_from_text(text)
        date_str = self._extract_header_from_text(text, "Date")  # e.g., "Wed, 25 Dec 2025 05:51:41 +0000"
        sender_name, _ = parseaddr(from_header) if from_header else ("", "")
        return {"subject": subject, "sender_name": sender_name, "body": body, 'date': date_str}

    def _extract_header_from_text(self, text, header_name):
        pattern = re.compile(rf"^{re.escape(header_name)}\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE | re.MULTILINE)
        match = pattern.search(text)
        if match:
            value = match.group(1).strip()
            return " ".join(value.split())
        return ""

    def _extract_message_body_from_text(self, text):
        lines = text.split("\n")
        body_start = 0
        header_pattern = re.compile(r"^\w+\s*:")
        for i, line in enumerate(lines):
            if header_pattern.match(line.strip()):
                body_start = i + 1
            elif line.strip() == "" and body_start > 0:
                body_start = i + 1
                break
        body_lines = [re.sub(r"^>\s*", "", l) for l in lines[body_start:]]
        body = "\n".join(body_lines).strip()
        body = re.split(r"\n--\s*\n", body)[0]
        return body

