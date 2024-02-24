import pytest
import sys

sys.path.append('src')
from data_generation import SampleBuilder 



class TestSampleBuilder:

    @pytest.fixture
    def builder_instance(self):
        builder = SampleBuilder()
        return builder

    def test_sample(self, builder_instance: SampleBuilder):

        # default sample state
        assert builder_instance.sample.frame_width == 20

        # yields current sample
        builder_instance._sample.frame_width = 40
        assert builder_instance.sample.frame_width == 40

        # reset on sample access
        assert builder_instance.sample.frame_width == 20

    def test_new_sample(self, builder_instance: SampleBuilder):

        
        pass

    def test_append_background_audio(self, builder_instance: SampleBuilder):
        pass

    def test_insert_damage_audio(self, builder_instance: SampleBuilder):
        pass

    def test_insert_audio(self, builder_instance: SampleBuilder):
        pass


def test_match_signals():
    pass
