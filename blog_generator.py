from openai import OpenAI
from pathlib import Path
from datetime import date
import config


class BlogGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.folder = config.BLOG_OUTPUT_DIR
        

    def generate_summary(self, html_content):
        print(html_content)
        '''
        response = self.client.responses.create(
            model="gpt-5-mini",
            input="Publishable technical blog from HTML content:\n\n" + html_content,
        )
        self.save_today_summary(response.output_text)

    def save_today_summary(self, summary: str) -> str:
        """
        Save summary to a folder as 'Summary for YYYY-MM-DD.txt'
        """
        today = date.today().isoformat()
        file_path = Path(self.folder) / f"Summary for {today}.txt"

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(summary, encoding="utf-8")

        return str(file_path)
        '''