"""
Module to select top threads based on activity and committer involvement.
"""
from typing import List, Dict


class ThreadSelector:
    """Selects top threads based on activity metrics and committer involvement."""
    
    def __init__(self, top_count: int = 5):
        self.top_count = top_count
    
    def select_top_threads(self, analyzed_threads: List[Dict]) -> List[Dict]:
        """
        Select top N threads based on activity score and committer involvement.
        
        Prioritizes threads with:
        1. High activity scores
        2. Committer participation
        3. Recent activity
        
        Args:
            analyzed_threads: List of thread dictionaries with metrics
            
        Returns:
            List of top N thread dictionaries
        """
        if not analyzed_threads:
            return []
        
        # Sort threads by priority:
        # 1. Has committers (higher priority)
        # 2. Activity score
        # 3. Recency (more recent = higher priority)
        
        def thread_priority(thread: Dict) -> tuple:
            has_committers = 1 if thread.get('committer_count', 0) > 0 else 0
            activity_score = thread.get('activity_score', 0)
            # Use end_date for recency (more recent = higher timestamp)
            recency = thread.get('end_date', thread.get('start_date'))
            recency_score = recency.timestamp() if hasattr(recency, 'timestamp') else 0
            
            return (
                -has_committers,  # Negative for descending sort (committers first)
                -activity_score,  # Negative for descending sort
                -recency_score    # Negative for descending sort
            )
        
        # Sort by priority
        sorted_threads = sorted(analyzed_threads, key=thread_priority)
        
        # Return top N
        return sorted_threads[:self.top_count]



