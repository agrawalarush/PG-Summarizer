"""
Module to sort and select top PostgreSQL threads for blog generation.
"""
from typing import List, Dict, Set
from datetime import datetime
import config


class ThreadSelector:
    """
    Selects and sorts threads based on committers activity,
    thread length, and overall activity duration.
    """

    def __init__(self, top_count: int = 10):
        """
        Args:
            top_count: Maximum number of threads to select
        """
        self.top_count = top_count
        # Convert committer names to lowercase set for easy matching
        self.committers: Set[str] = set(name.lower() for name in config.COMMITTERS)

    def select_top_threads(self, threads: List[Dict]) -> List[Dict]:
        """
        Sort threads and return top-N threads.
        """
        scored_threads = []
        for thread in threads:
            score = self._score_thread(thread)
            thread_copy = thread.copy()
            thread_copy["score"] = score
            scored_threads.append(thread_copy)

        # Sort descending by score
        scored_threads.sort(key=lambda t: t["score"], reverse=True)

        # Select top-N
        return scored_threads[:self.top_count]

    def _score_thread(self, thread: Dict) -> float:
        """
        Compute a score for a thread based on committers, number of messages,
        and duration.
        """
        messages = thread.get("messages", [])
        if not messages:
            return 0.0

        # Count unique committers participating
        committer_count = len(
            set(
                msg.get("sender_name", "").lower()
                for msg in messages
                if msg.get("sender_name") and msg["sender_name"].lower() in self.committers
            )
        )
        print(f"Thread '{thread.get('Thread_name','')}' has {committer_count} committers.")

        # Count total messages
        message_count = len(messages)

        # Thread duration in days
        dates = []
        for msg in messages:
            date_val = msg.get("date")
            if isinstance(date_val, datetime):
                dates.append(date_val)

        if dates:
            duration_days = (max(dates).date() - min(dates).date()).days
            duration_days = max(duration_days, 1)  # avoid zero
        else:
            duration_days = 1

        # Weighted scoring:
        # Committers participation is most important, then message count, then duration
        score = (committer_count * 3.0) + (message_count * 1.5) + (duration_days * 0.5)
        return score
