import logging

logger = logging.getLogger(__name__)

AWAITING_CONFIRMATION = "awaiting_confirmation"


class ConversationStore:
    """
    In-memory store of partial student data per sender.
    Tracks both partial data (for missing fields) and pending confirmation state.
    """

    def __init__(self):
        self._store: dict[str, dict] = {}

    def get(self, sender: str) -> dict:
        return self._store.get(sender, {})

    def merge(self, sender: str, new_data: dict) -> dict:
        """Merges new_data into existing partial data and returns the combined result."""
        existing = self._store.get(sender, {})
        merged = {**existing, **{k: v for k, v in new_data.items() if v}}
        self._store[sender] = merged
        logger.info("Conversation state for %s: %s", sender, merged)
        return merged

    def set_pending_confirmation(self, sender: str, data: dict) -> None:
        """Saves fully extracted data awaiting user confirmation before creating in Frappe."""
        self._store[sender] = {**data, "_state": AWAITING_CONFIRMATION}
        logger.info("Awaiting confirmation from %s", sender)

    def is_awaiting_confirmation(self, sender: str) -> bool:
        return self._store.get(sender, {}).get("_state") == AWAITING_CONFIRMATION

    def get_confirmed_data(self, sender: str) -> dict:
        """Returns the pending data without the internal _state key."""
        data = self._store.get(sender, {})
        return {k: v for k, v in data.items() if k != "_state"}

    def clear(self, sender: str) -> None:
        """Clears state after successful submission or cancellation."""
        self._store.pop(sender, None)
