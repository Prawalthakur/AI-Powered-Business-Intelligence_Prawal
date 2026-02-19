import pandas as pd

from src import utils


def test_chunk_text_overlap():
    text = "abcdefghij"
    chunks = utils.chunk_text(text, chunk_size=4, overlap=2)

    assert chunks == ["abcd", "cdef", "efgh", "ghij", "ij"]


def test_load_csv(tmp_path):
    csv_path = tmp_path / "data.csv"
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    df.to_csv(csv_path, index=False)

    loaded = utils.load_csv(str(csv_path))

    pd.testing.assert_frame_equal(loaded, df)


def test_save_csv_uses_target_directory(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    monkeypatch.setattr(utils, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(utils, "PROCESSED_DATA_DIR", processed_dir)

    df = pd.DataFrame({"col": [1]})

    raw_path = utils.save_csv(df, "raw.csv", folder="raw")
    processed_path = utils.save_csv(df, "processed.csv")

    assert raw_path == raw_dir / "raw.csv"
    assert processed_path == processed_dir / "processed.csv"
    assert raw_path.exists()
    assert processed_path.exists()
