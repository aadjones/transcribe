from benchmarks.benchmark import get_transformations


def test_reference_transformation_no_punctuation():
    # Ground truth is expected to have no punctuation and to be in uppercase,
    # but we apply a transformation that lowercases everything.
    reference = "HELLO WORLD"
    expected = [["hello", "world"]]
    ref_transform, _ = get_transformations()
    result = ref_transform([reference])
    assert result == expected, f"Expected {expected} but got {result}"


def test_hypothesis_transformation_removes_hyphen():
    # The hypothesis may include hyphens that should be replaced by spaces.
    hypothesis = "hello-world"
    expected = [["hello", "world"]]
    _, hyp_transform = get_transformations()
    result = hyp_transform([hypothesis])
    assert result == expected, f"Expected {expected} but got {result}"


def test_hypothesis_transformation_removes_punctuation():
    hypothesis = "hello, world!"
    expected = [["hello", "world"]]
    _, hyp_transform = get_transformations()
    result = hyp_transform([hypothesis])
    assert result == expected, f"Expected {expected} but got {result}"


def test_mixed_transformation():
    # Test a case that involves both hyphens and punctuation.
    hypothesis = "But if I play you-around, will you come?"
    # Expected: hyphen replaced with space, punctuation removed, then lowercased.
    expected = [["but", "if", "i", "play", "you", "around", "will", "you", "come"]]
    _, hyp_transform = get_transformations()
    result = hyp_transform([hypothesis])
    assert result == expected, f"Expected {expected} but got {result}"
