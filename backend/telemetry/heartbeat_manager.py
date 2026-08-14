import asyncio
import time
from typing import Set, Dict, Any
from fastapi import WebSocket
from .ws_metrics import ws_metrics

class HeartbeatManager:
    """Manages 15-second heartbeat ping/pongs and stale WebSocket cleanup."""

    def __init__(self, heartbeat_interval: float = 15.0):
        self.heartbeat_interval = heartbeat_interval
        self._running = False
        self._task: asyncio.Task = None

    async def start(self, manager_broadcast_fn):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._heartbeat_loop(manager_broadcast_fn))

    async def stop(self):
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    async def _heartbeat_loop(self, manager_broadcast_fn):
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                ws_metrics.record_heartbeat()
                payload = {
                    "type": "heartbeat",
                    "timestamp": time.time(),
                    "status": "ping"
                }
                await manager_broadcast_fn(payload)
            except asyncio.CancelledError:
                break
            except Exception as e:
                pass

# Global Singleton
heartbeat_manager = HeartbeatManager()
