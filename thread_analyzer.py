"""
Module to analyze email threads, group messages, and calculate activity metrics.
"""
import re
from typing import List, Dict, Set
from collections import defaultdict
from datetime import datetime


class ThreadAnalyzer:
    """Analyzes email threads and calculates activity metrics."""
    
    def __init__(self, committers: Set[str]):
        self.committers = committers
    
    def group_messages_into_threads(self, messages: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group messages into threads based on Subject and References/In-Reply-To.
        
        Args:
            messages: List of parsed message dictionaries
            
        Returns:
            Dictionary mapping thread_id to list of messages
        """
        threads = defaultdict(list)
        message_map = {msg['message_id']: msg for msg in messages}
        
        # Normalize subject for thread grouping
        def normalize_subject(subject: str) -> str:
            # Remove Re:, Fwd:, etc.
            subject = re.sub(r'^(Re:|Fwd?:|RE:|FW:)\s*', '', subject, flags=re.IGNORECASE)
            # Remove [tag] prefixes
            subject = re.sub(r'^\[.*?\]\s*', '', subject)
            return subject.strip()
        
        # Build thread relationships
        for msg in messages:
            thread_id = None
            
            # Try to find thread via In-Reply-To or References
            if msg['in_reply_to']:
                # Find parent message
                parent = message_map.get(msg['in_reply_to'])
                if parent:
                    # Use parent's thread_id if it exists
                    for tid, msgs in threads.items():
                        if parent in msgs:
                            thread_id = tid
                            break
            
            # If no thread found, check References header
            if not thread_id and msg['references']:
                ref_ids = [ref.strip() for ref in msg['references'].split()]
                for ref_id in reversed(ref_ids):  # Check from most recent
                    for tid, msgs in threads.items():
                        if any(m['message_id'] == ref_id for m in msgs):
                            thread_id = tid
                            break
                    if thread_id:
                        break
            
            # If still no thread, create new one based on normalized subject
            if not thread_id:
                normalized_subject = normalize_subject(msg['subject'])
                # Try to find existing thread with same normalized subject
                for tid, msgs in threads.items():
                    if normalize_subject(msgs[0]['subject']) == normalized_subject:
                        thread_id = tid
                        break
                
                if not thread_id:
                    thread_id = msg['message_id']  # Use first message ID as thread ID
            
            threads[thread_id].append(msg)
        
        # Sort messages in each thread by date
        for thread_id in threads:
            threads[thread_id].sort(key=lambda m: m['date'])
        
        return dict(threads)
    
    def calculate_thread_metrics(self, thread_messages: List[Dict]) -> Dict:
        """
        Calculate activity metrics for a thread.
        
        Args:
            thread_messages: List of messages in the thread
            
        Returns:
            Dictionary with metrics
        """
        if not thread_messages:
            return {}
        
        # Count messages
        message_count = len(thread_messages)
        
        # Count unique participants
        participants = set()
        committer_participants = set()
        
        for msg in thread_messages:
            email = msg['sender_email'].lower()
            participants.add(email)
            
            # Check if sender is a committer
            if self._is_committer(email):
                committer_participants.add(email)
        
        # Calculate activity score
        activity_score = (
            message_count * 1.0 +
            len(committer_participants) * 2.0 +
            len(participants) * 0.5
        )
        
        # Get thread dates
        dates = [msg['date'] for msg in thread_messages]
        start_date = min(dates)
        end_date = max(dates)
        
        # Get thread subject (from first message)
        subject = thread_messages[0]['subject']
        
        return {
            'message_count': message_count,
            'unique_participants': len(participants),
            'committer_count': len(committer_participants),
            'committer_emails': list(committer_participants),
            'participant_emails': list(participants),
            'activity_score': activity_score,
            'start_date': start_date,
            'end_date': end_date,
            'subject': subject,
            'messages': thread_messages
        }
    
    def _is_committer(self, email: str) -> bool:
        """Check if an email belongs to a PostgreSQL committer."""
        email_lower = email.lower()
        return any(committer.lower() in email_lower or email_lower in committer.lower() 
                  for committer in self.committers)
    
    def analyze_all_threads(self, messages: List[Dict]) -> List[Dict]:
        """
        Analyze all threads and return sorted list by activity.
        
        Args:
            messages: List of parsed message dictionaries
            
        Returns:
            List of thread dictionaries with metrics, sorted by activity score
        """
        threads = self.group_messages_into_threads(messages)
        
        analyzed_threads = []
        for thread_id, thread_messages in threads.items():
            metrics = self.calculate_thread_metrics(thread_messages)
            if metrics:
                metrics['thread_id'] = thread_id
                analyzed_threads.append(metrics)
        
        # Sort by activity score (descending)
        analyzed_threads.sort(key=lambda t: t['activity_score'], reverse=True)
        
        return analyzed_threads



