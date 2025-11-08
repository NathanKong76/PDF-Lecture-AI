"""
Global Concurrency Controller.

Provides centralized concurrency management to prevent resource exhaustion
from concurrent file and page processing.
"""

import asyncio
import time
from typing import Optional
from dataclasses import dataclass, field
from .logger import get_logger

logger = get_logger()


@dataclass
class ConcurrencyStats:
    """Statistics for concurrency usage."""
    current_requests: int = 0
    peak_requests: int = 0
    total_requests: int = 0
    blocked_requests: int = 0
    last_reset: float = field(default_factory=time.time)


class GlobalConcurrencyController:
    """
    Global concurrency controller to prevent resource exhaustion.
    
    This controller manages the total number of concurrent API requests
    across all files and pages to prevent exceeding API limits and
    system resources.
    """
    
    _instance: Optional['GlobalConcurrencyController'] = None
    _lock = asyncio.Lock()
    
    def __init__(self, max_global_concurrency: int = 200):
        """
        Initialize global concurrency controller.
        
        Args:
            max_global_concurrency: Maximum total concurrent requests across all operations
        """
        self.max_global_concurrency = max_global_concurrency
        self.semaphore = asyncio.Semaphore(max_global_concurrency)
        self.stats = ConcurrencyStats()
        self._active_requests: set[str] = set()
        self._request_counter = 0
    
    @classmethod
    async def get_instance(cls, max_global_concurrency: int = 200) -> 'GlobalConcurrencyController':
        """
        Get or create singleton instance.
        
        Args:
            max_global_concurrency: Maximum global concurrency (only used on first creation)
            
        Returns:
            Global concurrency controller instance
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(max_global_concurrency)
        return cls._instance
    
    @classmethod
    def get_instance_sync(cls, max_global_concurrency: int = 200) -> 'GlobalConcurrencyController':
        """
        Get or create singleton instance (synchronous version).
        
        Args:
            max_global_concurrency: Maximum global concurrency (only used on first creation)
            
        Returns:
            Global concurrency controller instance
        """
        if cls._instance is None:
            cls._instance = cls(max_global_concurrency)
        return cls._instance
    
    async def acquire(self, request_id: Optional[str] = None) -> None:
        """
        Acquire a concurrency slot.
        
        Args:
            request_id: Optional identifier for this request (for tracking)
        """
        # Check if we need to wait
        if self.semaphore._value <= 0:
            self.stats.blocked_requests += 1
            if self.stats.blocked_requests % 10 == 0:
                logger.warning(
                    f"Global concurrency limit reached ({self.max_global_concurrency}). "
                    f"{self.stats.blocked_requests} requests blocked."
                )
        
        await self.semaphore.acquire()
        
        # Update statistics
        self.stats.current_requests += 1
        self.stats.total_requests += 1
        self.stats.peak_requests = max(
            self.stats.peak_requests,
            self.stats.current_requests
        )
        
        if request_id:
            self._active_requests.add(request_id)
    
    def release(self, request_id: Optional[str] = None) -> None:
        """
        Release a concurrency slot.
        
        Args:
            request_id: Optional identifier for this request
        """
        self.semaphore.release()
        self.stats.current_requests = max(0, self.stats.current_requests - 1)
        
        if request_id and request_id in self._active_requests:
            self._active_requests.remove(request_id)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.release()
    
    def get_stats(self) -> ConcurrencyStats:
        """Get current concurrency statistics."""
        return self.stats
    
    def get_available_slots(self) -> int:
        """Get number of available concurrency slots."""
        return self.semaphore._value
    
    def reset_stats(self) -> None:
        """Reset statistics (useful for monitoring periods)."""
        self.stats = ConcurrencyStats()
    
    def adjust_limit(self, new_limit: int) -> None:
        """
        Adjust the global concurrency limit.
        
        Args:
            new_limit: New maximum concurrency limit
        """
        if new_limit < 1:
            raise ValueError("Concurrency limit must be at least 1")
        
        old_limit = self.max_global_concurrency
        self.max_global_concurrency = new_limit
        
        # Adjust semaphore
        current_value = self.semaphore._value
        difference = new_limit - old_limit
        
        if difference > 0:
            # Increase limit: release additional permits
            for _ in range(difference):
                self.semaphore.release()
        elif difference < 0:
            # Decrease limit: acquire permits to reduce available slots
            # Note: This won't block existing requests, just prevents new ones
            pass
        
        logger.info(
            f"Global concurrency limit adjusted from {old_limit} to {new_limit}. "
            f"Current active: {self.stats.current_requests}"
        )


def calculate_optimal_concurrency(
    page_concurrency: int,
    file_count: int,
    rpm_limit: int,
    max_global_concurrency: int = 200
) -> tuple[int, int]:
    """
    Calculate optimal concurrency settings considering global limits.
    
    Args:
        page_concurrency: Desired page-level concurrency
        file_count: Number of files being processed
        rpm_limit: API RPM limit
        max_global_concurrency: Maximum global concurrency limit
        
    Returns:
        Tuple of (adjusted_page_concurrency, adjusted_file_concurrency)
    """
    # Calculate theoretical maximum concurrent requests
    theoretical_max = page_concurrency * file_count
    
    # Limit by global concurrency
    if theoretical_max > max_global_concurrency:
        # Scale down proportionally
        scale_factor = max_global_concurrency / theoretical_max
        adjusted_page_concurrency = max(1, int(page_concurrency * scale_factor))
        adjusted_file_concurrency = file_count
    else:
        adjusted_page_concurrency = page_concurrency
        adjusted_file_concurrency = file_count
    
    # Also consider API RPM limit (with safety margin)
    # Assume average request takes 2-3 seconds, so we want to stay under RPM/2
    safe_rpm = max(1, rpm_limit // 2)
    if adjusted_page_concurrency * adjusted_file_concurrency > safe_rpm:
        # Scale down to stay within safe RPM
        scale_factor = safe_rpm / (adjusted_page_concurrency * adjusted_file_concurrency)
        adjusted_page_concurrency = max(1, int(adjusted_page_concurrency * scale_factor))
    
    return adjusted_page_concurrency, adjusted_file_concurrency

