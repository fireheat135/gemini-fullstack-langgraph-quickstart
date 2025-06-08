"""
Rate limiting functionality for API endpoints
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
import time


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[str, list] = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            True if within limit, False if exceeded
        """
        now = time.time()
        
        # Clean old calls
        self._clean_old_calls(client_id, now)
        
        # Check if limit exceeded
        if len(self.calls[client_id]) >= self.max_calls:
            return False
        
        # Record this call
        self.calls[client_id].append(now)
        return True
    
    def get_remaining_calls(self, client_id: str) -> int:
        """Get number of remaining calls for client"""
        now = time.time()
        self._clean_old_calls(client_id, now)
        return max(0, self.max_calls - len(self.calls[client_id]))
    
    def get_reset_time(self, client_id: str) -> datetime:
        """Get time when rate limit resets for client"""
        if not self.calls[client_id]:
            return datetime.now()
        
        oldest_call = min(self.calls[client_id])
        reset_timestamp = oldest_call + self.time_window
        return datetime.fromtimestamp(reset_timestamp)
    
    def _clean_old_calls(self, client_id: str, current_time: float):
        """Remove calls outside the time window"""
        cutoff_time = current_time - self.time_window
        self.calls[client_id] = [
            call_time for call_time in self.calls[client_id]
            if call_time > cutoff_time
        ]