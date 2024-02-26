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
        assert builder_instance.get_sample.frame_width == 20

        # yields current sample
        builder_instance._sample.frame_width = 40
        assert builder_instance.get_sample.frame_width == 40

        # reset on sample access
        assert builder_instance.get_sample.frame_width == 20

    def test_new_sample(self, builder_instance: SampleBuilder):

        
        pass

    def test_append_background_audio(self, builder_instance: SampleBuilder):

        # check that different samplerates are properly handled
        sr1 = 100
        sr2 = 200
        builder_instance._sample.audio_wave_form = list(range(0,100))
        builder_instance._sample.audio_sample_rate = sr1
        initial_audio_length = len(builder_instance._sample.audio_wave_form)

        builder_instance.append_background_audio(list(range(0,25)), sr2, 5000, 2)
        sample = builder_instance._sample
        scale_factor = float(sr2/sr1)
        assert sample.audio_sample_rate != sr1
        assert sample.audio_sample_rate == sr2
        assert len(sample.audio_wave_form) != int(scale_factor * initial_audio_length)



    def test_insert_damage_audio(self, builder_instance: SampleBuilder):
        pass

    def test_insert_audio(self, builder_instance: SampleBuilder):
        pass


def test_match_signals():
    pass
