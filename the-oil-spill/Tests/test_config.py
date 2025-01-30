import pytest
from config import ReadConfig

@pytest.fixture
def conf():
    return ReadConfig("configurations\example.toml")

def test_solution(conf):
    solutuon = conf.find_solution()
    assert solutuon[0] == 0.0, " test_start should be 0.0 but isnt"
    assert solutuon[1] == [], "oil list should be empty but isnt"