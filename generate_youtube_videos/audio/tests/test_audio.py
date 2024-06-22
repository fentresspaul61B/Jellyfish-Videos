import pandas as pd
from icecream import ic
import tempfile
import os
from generate_youtube_videos.audio.generation import generate_raw_audio_files

HISTORY_CSV = "generate_youtube_videos/audio/tests/files_for_testing/Jellyfish.csv"
TESTING_DF = pd.read_csv(HISTORY_CSV, index_col=0)


def test_generate_raw_audio_files():
    with tempfile.TemporaryDirectory() as temp_output_dir:
        result_dir = generate_raw_audio_files(HISTORY_CSV, temp_output_dir)

        files = os.listdir(result_dir)
        assert len(files) > 0, "No files generated in the output directory."


def main():
    pass


if __name__ == "__main__":
    main()
