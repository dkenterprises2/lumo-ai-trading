from typing import Dict, Any, List

class TimeSeriesCrossValidator:
    """Purged & Embargoed Time-Series Cross Validation."""

    @staticmethod
    def get_split_indices(n_samples: int = 1000, n_splits: int = 5) -> List[Dict[str, Any]]:
        splits = []
        step = n_samples // (n_splits + 1)
        for i in range(1, n_splits + 1):
            splits.append({
                "fold": i,
                "train_end": i * step,
                "test_start": i * step + 10, # Embargo gap
                "test_end": (i + 1) * step
            })
        return splits

time_series_cv = TimeSeriesCrossValidator()
