import pytest
from ..app.calculate_sqrt import calculate_sqrt

def test_calculate_sqrt_pass():
    assert calculate_sqrt(9) == 3

def test_calculate_sqrt_edge():
    assert calculate_sqrt(0) == 0

def test_calculate_sqrt_fail():
    assert calculate_sqrt(16) == 5  # This test is intentionally incorrect
