from benchmarks.benchmark_utils import minimal_transform


def test_minimal_transform():
    # This is the reference transcript text.
    transcript = "Marrow signal alteration in the clavicle with cortical erosion and surrounding soft tissue edema."
    # Expected result: a list of words as produced by the original minimal transform.
    expected = [
        "Marrow",
        "signal",
        "alteration",
        "in",
        "the",
        "clavicle",
        "with",
        "cortical",
        "erosion",
        "and",
        "surrounding",
        "soft",
        "tissue",
        "edema.",
    ]
    # minimal_transform expects a list of strings, so we pass [transcript].
    result = minimal_transform([transcript])[0]
    assert result == expected
