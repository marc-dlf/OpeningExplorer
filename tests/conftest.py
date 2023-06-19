"""Conftest file for omni_ai unit tests."""
import pytest


@pytest.fixture
def dummy_pgn():  # pragma: no cover
    sample_pgn_path = "tests/units/data_examples/dummy_pgn.txt"
    with open(sample_pgn_path, "r") as f:
        return f.read()


@pytest.fixture
def complete_pgn():  # pragma: no cover
    sample_pgn_path = "tests/units/data_examples/complete_pgn.txt"
    with open(sample_pgn_path, "r") as f:
        return f.read()


@pytest.fixture
def username():  # pragma: no cover
    return "marcov24"


@pytest.fixture
def csv_path():  # pragma: no cover
    return "tests/units/data_examples/example_player.csv"
