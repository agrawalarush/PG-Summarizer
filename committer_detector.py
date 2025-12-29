"""
Module to detect and maintain list of PostgreSQL committers.
Fetches committer information from PostgreSQL project sources.
"""
import os
import requests
import re
from typing import Set
from bs4 import BeautifulSoup

import config


class CommitterDetector:
    """Detects and maintains list of PostgreSQL committers."""
    
    def __init__(self):
        self.committers_file = config.COMMITTERS_FILE
        self.committers: Set[str] = set()
        self._load_committers()
    
    def _load_committers(self):
        """Load committers from file or fetch from web."""
        try:
            # Try to load from file
            if os.path.exists(self.committers_file):
                with open(self.committers_file, 'r') as f:
                    self.committers = {line.strip() for line in f if line.strip()}
        except Exception:
            pass
        
        # If file doesn't exist or is empty, fetch from web
        if not self.committers:
            self._fetch_committers_from_web()
            self._save_committers()
    
    def _fetch_committers_from_web(self):
        """Fetch list of PostgreSQL committers from project website."""
        # PostgreSQL committers page
        urls = [
            "https://www.postgresql.org/developer/committers/"
        ]
        
        committers = set()
        
        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract email addresses and names
                # Look for common patterns in committer listings
                text = soup.get_text()
                
                # Extract email patterns
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, text)
                committers.update(emails)
                
                # Also look for names that might be in committer lists
                # This is a simplified approach - in production, you'd want
                # to parse the actual committer list more carefully
                
            except Exception as e:
                print(f"Error fetching committers from {url}: {e}")
        
        # Add known committer patterns/domains
        # PostgreSQL committers often use specific email patterns
        known_patterns = [
            '@postgresql.org',
            '@enterprisedb.com',
            '@2ndquadrant.com',
            '@timescale.com',
        ]
        
        # Also maintain a manual list of known committers
        # This should be updated periodically
        known_committers = [
            'tgl@sss.pgh.pa.us',  # Tom Lane
            'andres@anarazel.de',  # Andres Freund
            'robertmhaas@gmail.com',  # Robert Haas
            'alvherre@alvh.no-ip.org',  # Alvaro Herrera
            'heikki.linnakangas@iki.fi',  # Heikki Linnakangas
            # Add more as needed
        ]
        
        committers.update(known_committers)
        self.committers = committers
    
    def _save_committers(self):
        """Save committers list to file."""
        try:
            os.makedirs(os.path.dirname(self.committers_file), exist_ok=True)
            with open(self.committers_file, 'w') as f:
                for committer in sorted(self.committers):
                    f.write(f"{committer}\n")
        except Exception as e:
            print(f"Error saving committers: {e}")
    
    def get_committers(self) -> Set[str]:
        """Get current list of committers."""
        return self.committers.copy()
    
    def update_committers(self):
        """Update committers list from web sources."""
        self._fetch_committers_from_web()
        self._save_committers()

