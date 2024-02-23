import pytest
import sys

sys.path.append('src')
from data_generation import SampleBuilder 


class TestSampleBuilder:

    def __init__(self):
        self.builder = SampleBuilder()
    

def test_match_signals():
    