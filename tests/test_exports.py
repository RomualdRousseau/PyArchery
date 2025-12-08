
import pytest

try:
    import pandas as pd
except ImportError:
    pd = None

import pyarchery


@pytest.mark.skipif(pd is None, reason="pandas not installed")
def test_to_pandas():
    """Test converting a table to a pandas DataFrame."""
    file_path = "examples/data/document with simple table.xlsx"
    with pyarchery.load(file_path, hints=[pyarchery.INTELLI_EXTRACT]) as doc:
        sheet = next(doc.sheets)
        table = sheet.table
        df = table.to_pandas()

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (4, 4)
        assert list(df.columns) == ["Date", "Client", "Qty", "Amount"]
        assert df["Date"].tolist() == [
            "2023-02-01",
            "2023-02-01",
            "2023-02-01",
            "2023-02-01",
        ]
        assert df["Client"].tolist() == ["AAA", "BBB", "BBB", "AAA"]
        assert df["Qty"].tolist() == ["1", "1", "3", "1"]
        assert df["Amount"].tolist() == ["100", "100", "300", "100"]

