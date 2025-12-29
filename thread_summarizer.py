"""
Module to generate detailed summaries of email threads,
focusing on design discussions and progress.
"""
from typing import Dict, List
from datetime import datetime
import re


class ThreadSummarizer:
    """Generates detailed summaries of email threads."""
    
    def summarize_thread(self, thread: Dict) -> Dict:
        """
        Generate a detailed summary of a thread.
        
        Args:
            thread: Thread dictionary with messages and metrics
            
        Returns:
            Dictionary with summary information
        """
        messages = thread.get('messages', [])
        if not messages:
            return {}
        
        # Extract key information
        subject = thread.get('subject', '')
        start_date = thread.get('start_date')
        end_date = thread.get('end_date')
        participants = thread.get('participant_emails', [])
        committers = thread.get('committer_emails', [])
        
        # Analyze discussion content
        discussion_points = self._extract_discussion_points(messages)
        design_decisions = self._extract_design_decisions(messages)
        progress_items = self._extract_progress_items(messages)
        action_items = self._extract_action_items(messages)
        
        # Generate summary text
        summary_text = self._generate_summary_text(
            subject, messages, discussion_points, design_decisions,
            progress_items, action_items, committers
        )
        
        return {
            'subject': subject,
            'start_date': start_date,
            'end_date': end_date,
            'participants': participants,
            'committers': committers,
            'message_count': thread.get('message_count', 0),
            'discussion_points': discussion_points,
            'design_decisions': design_decisions,
            'progress_items': progress_items,
            'action_items': action_items,
            'summary_text': summary_text,
            'thread_id': thread.get('thread_id', '')
        }
    
    def _extract_discussion_points(self, messages: List[Dict]) -> List[str]:
        """Extract key discussion points from messages."""
        discussion_points = []
        
        for msg in messages:
            body = msg.get('body', '')
            subject = msg.get('subject', '')
            
            # Look for questions, proposals, concerns
            # This is a simplified extraction - could be enhanced with NLP
            lines = body.split('\n')
            for line in lines[:50]:  # Check first 50 lines
                line = line.strip()
                if len(line) > 20 and len(line) < 500:
                    # Look for discussion indicators
                    if any(indicator in line.lower() for indicator in [
                        'propose', 'suggest', 'question', 'concern', 'issue',
                        'problem', 'consider', 'think', 'opinion', 'discuss'
                    ]):
                        # Clean up the line
                        line = re.sub(r'^[>|]\s*', '', line)  # Remove quote markers
                        if line and line not in discussion_points:
                            discussion_points.append(line[:200])  # Limit length
        
        return discussion_points[:10]  # Top 10 discussion points
    
    def _extract_design_decisions(self, messages: List[Dict]) -> List[str]:
        """Extract design decisions and conclusions from messages."""
        decisions = []
        
        for msg in messages:
            body = msg.get('body', '')
            
            # Look for decision indicators
            decision_patterns = [
                r'decided to',
                r'we should',
                r'we will',
                r'agreed to',
                r'consensus is',
                r'decision:',
                r'conclusion:',
                r'we\'ll',
                r'going with',
                r'chosen to'
            ]
            
            lines = body.split('\n')
            for line in lines:
                line = line.strip()
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in decision_patterns):
                    line = re.sub(r'^[>|]\s*', '', line)
                    if line and len(line) > 20 and len(line) < 500:
                        decisions.append(line[:200])
        
        return decisions[:10]
    
    def _extract_progress_items(self, messages: List[Dict]) -> List[str]:
        """Extract progress updates and status changes."""
        progress_items = []
        
        for msg in messages:
            body = msg.get('body', '')
            
            # Look for progress indicators
            progress_patterns = [
                r'completed',
                r'finished',
                r'implemented',
                r'added',
                r'fixed',
                r'resolved',
                r'updated',
                r'progress',
                r'status:',
                r'done'
            ]
            
            lines = body.split('\n')
            for line in lines:
                line = line.strip()
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in progress_patterns):
                    line = re.sub(r'^[>|]\s*', '', line)
                    if line and len(line) > 20 and len(line) < 500:
                        progress_items.append(line[:200])
        
        return progress_items[:10]
    
    def _extract_action_items(self, messages: List[Dict]) -> List[str]:
        """Extract action items and TODO items."""
        action_items = []
        
        for msg in messages:
            body = msg.get('body', '')
            
            # Look for action item indicators
            action_patterns = [
                r'action:',
                r'todo:',
                r'need to',
                r'should do',
                r'will do',
                r'next step',
                r'follow up'
            ]
            
            lines = body.split('\n')
            for line in lines:
                line = line.strip()
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in action_patterns):
                    line = re.sub(r'^[>|]\s*', '', line)
                    if line and len(line) > 20 and len(line) < 500:
                        action_items.append(line[:200])
        
        return action_items[:10]
    
    def _generate_summary_text(self, subject: str, messages: List[Dict],
                              discussion_points: List[str],
                              design_decisions: List[str],
                              progress_items: List[str],
                              action_items: List[str],
                              committers: List[str]) -> str:
        """Generate a comprehensive summary text."""
        summary_parts = []
        
        # Introduction
        summary_parts.append(f"## Thread: {subject}\n")
        
        # Committer involvement
        if committers:
            committer_list = ', '.join(committers[:5])
            summary_parts.append(f"**PostgreSQL Committers Involved:** {committer_list}\n")
        
        # Discussion overview
        if discussion_points:
            summary_parts.append("### Key Discussion Points\n")
            for i, point in enumerate(discussion_points[:5], 1):
                summary_parts.append(f"{i}. {point}\n")
        
        # Design decisions
        if design_decisions:
            summary_parts.append("\n### Design Decisions\n")
            for i, decision in enumerate(design_decisions[:5], 1):
                summary_parts.append(f"{i}. {decision}\n")
        
        # Progress updates
        if progress_items:
            summary_parts.append("\n### Progress Updates\n")
            for i, progress in enumerate(progress_items[:5], 1):
                summary_parts.append(f"{i}. {progress}\n")
        
        # Action items
        if action_items:
            summary_parts.append("\n### Action Items\n")
            for i, action in enumerate(action_items[:5], 1):
                summary_parts.append(f"{i}. {action}\n")
        
        # Thread statistics
        summary_parts.append(f"\n**Thread Statistics:**\n")
        summary_parts.append(f"- Total Messages: {len(messages)}\n")
        summary_parts.append(f"- Participants: {len(set(m.get('sender_email', '') for m in messages))}\n")
        
        return '\n'.join(summary_parts)



