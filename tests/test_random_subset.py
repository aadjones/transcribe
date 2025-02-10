# tests/test_random_subset.py

from benchmarks.benchmark_utils import get_random_subset


def test_get_random_subset_returns_correct_length():
    dataset = list(range(100))
    subset = get_random_subset(dataset, 10)
    assert (
        len(subset) == 10
    ), "Subset length should equal max_samples when dataset is larger."


def test_get_random_subset_returns_all_items_if_max_none():
    dataset = list(range(50))
    subset = get_random_subset(dataset, None)
    assert subset == dataset, "If max_samples is None, all items should be returned."


def test_get_random_subset_fixed_seed(monkeypatch):
    import time

    dataset = list(range(100))

    # Force time.time() to always return a constant value.
    monkeypatch.setattr(time, "time", lambda: 42)

    subset1 = get_random_subset(dataset, 10)
    subset2 = get_random_subset(dataset, 10)

    assert (
        subset1 == subset2
    ), "Repeated calls with a fixed time (and thus fixed seed) should yield the same subset."
