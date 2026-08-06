import time
import requests
from typing import Dict, Any, Optional, List
from backend.core.logger import logger

class AlertManager:
    """Multi-Channel Production Alerting & Notification Engine (Telegram, Discord, Webhooks)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlertManager, cls).__new__(cls)
            cls._instance._init_alerting()
        return cls._instance

    def _init_alerting(self):
        self.telegram_bot_token: Optional[str] = None
        self.telegram_chat_id: Optional[str] = None
        self.discord_webhook_url: Optional[str] = None
        self.generic_webhook_url: Optional[str] = None

    def configure(self, telegram_token: Optional[str] = None, telegram_chat_id: Optional[str] = None, discord_webhook: Optional[str] = None, generic_webhook: Optional[str] = None):
        self.telegram_bot_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.discord_webhook_url = discord_webhook
        self.generic_webhook_url = generic_webhook

    def send_alert(self, alert_type: str, title: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatch alert to configured Telegram, Discord, and Webhook destinations."""
        payload = {
            "alert_type": alert_type,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "timestamp": time.time()
        }

        delivered_channels = []

        # 1. Telegram Dispatch
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                text = f"<b>[{title}]</b>\n{message}"
                requests.post(url, json={"chat_id": self.telegram_chat_id, "text": text, "parse_mode": "HTML"}, timeout=3.0)
                delivered_channels.append("TELEGRAM")
            except Exception as e:
                logger.error(f"[ALERT_ERROR] Telegram dispatch failed: {e}")

        # 2. Discord Dispatch
        if self.discord_webhook_url:
            try:
                discord_payload = {
                    "embeds": [{
                        "title": f"🚀 LUMO ALERT: {title}",
                        "description": message,
                        "color": 3066993 if alert_type != "CRITICAL_ERROR" else 15158332
                    }]
                }
                requests.post(self.discord_webhook_url, json=discord_payload, timeout=3.0)
                delivered_channels.append("DISCORD")
            except Exception as e:
                logger.error(f"[ALERT_ERROR] Discord dispatch failed: {e}")

        # 3. Generic Webhook
        if self.generic_webhook_url:
            try:
                requests.post(self.generic_webhook_url, json=payload, timeout=3.0)
                delivered_channels.append("GENERIC_WEBHOOK")
            except Exception as e:
                logger.error(f"[ALERT_ERROR] Generic Webhook dispatch failed: {e}")

        return {
            "status": "success",
            "alert_type": alert_type,
            "delivered_channels": delivered_channels,
            "payload": payload
        }

alert_manager = AlertManager()
