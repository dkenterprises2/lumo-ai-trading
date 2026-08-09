from typing import Dict, Any, List

class ExperienceReplayBuffer:
    """Prioritized Trajectory Experience Replay Buffer."""

    def __init__(self):
        self._buffer: List[Dict[str, Any]] = []

    def add_experience(self, obs: dict, action: str, reward: float, next_obs: dict, done: bool):
        self._buffer.append({
            "obs": obs,
            "action": action,
            "reward": reward,
            "next_obs": next_obs,
            "done": done
        })

    def sample_batch(self, batch_size: int = 32) -> List[Dict[str, Any]]:
        return self._buffer[:batch_size]

    def size(self) -> int:
        return len(self._buffer)

experience_replay = ExperienceReplayBuffer()
