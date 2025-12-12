from pathlib import Path

import pandas as pd

import pyarchery

REPO_BASE_URL = "https://raw.githubusercontent.com/RomualdRousseau/Archery/main/archery-models"
MODEL_NAME = "sales-english"
FILE_PATH = Path(__file__).parent / "data" / "document with multiple tables.xlsx"
FILE_ENCODING = "UTF-8"
EXPECTED_TABLE = Path(__file__).parent / "data" / "test_load_expected.md"
DATA_DIR = Path(__file__).parent / "data"


def test_load_and_wrappers():
    filenames = [
        "document with simple table.csv",
        "document with simple table.xlsx",
        "document with simple table.xls",
    ]
    for filename in filenames:
        file_path = DATA_DIR / filename

        with pyarchery.load(file_path) as doc:
            sheets = list(doc.sheets)
            assert len(sheets) > 0

            sheet = sheets[0]
            table = sheet.table
            assert table is not None

            data_dict = table.to_pydict()
            assert isinstance(data_dict, dict)
            assert len(data_dict) > 0
            assert set(data_dict.keys()) == set(table.header_names)

            arrow_table = table.to_arrow()
            assert arrow_table.num_rows > 0
            assert arrow_table.num_columns == len(table.headers)

            df = table.to_arrow().to_pandas()
            assert isinstance(df, pd.DataFrame)
            assert not df.empty
            assert len(df) == arrow_table.num_rows

            rows = list(table.rows)
            assert len(rows) == arrow_table.num_rows
            # ensure row iteration yields cell wrappers
            for row in rows:
                assert len(row.cells) == len(table.headers)
                for cell in row:
                    assert cell.value is not None

            # ensure headers expose tag_value (may be None if tag absent)
            for header in table.headers:
                _ = header.tag_value

            output_csv = DATA_DIR / f"test_output_{filename}.csv"
            try:
                table.to_csv(output_csv)
                assert output_csv.exists()
                assert output_csv.stat().st_size > 0
            finally:
                if output_csv.exists():
                    output_csv.unlink()


def _build_model():
    builder = pyarchery.model_from_url(f"{REPO_BASE_URL}/{MODEL_NAME}/{MODEL_NAME}.json")

    entities = [v for v in builder.getEntityList() if v != "PACKAGE"]
    entities.append("PRODUCTNAME")

    patterns = {k: v for (k, v) in builder.getPatternMap().items() if v != "PACKAGE"}
    patterns["\\D+\\dml"] = "PRODUCTNAME"

    parser = pyarchery.LayexTableParser(["(v.$)+"], ["(()(S+$))(()([/^TOTAL/|v].+$)())+(/TOTAL/.+$)"])

    return builder.setEntityList(entities).setPatternMap(patterns).setTableParser(parser).build()


def test_load_model_from_url_and_extract_tables():
    """Ensure loading with a remote model yields expected table contents."""
    model = _build_model()
    expected_markdown = EXPECTED_TABLE.read_text().strip()

    with pyarchery.load(
        FILE_PATH,
        encoding=FILE_ENCODING,
        model=model,
        hints=[pyarchery.INTELLI_LAYOUT, pyarchery.INTELLI_TIME],
        recipe=["sheet.setCapillarityThreshold(0)"],
        tag_case="SNAKE",
    ) as doc:
        tables = []
        for sheet in doc.sheets:
            table = sheet.table
            if table:
                df = table.to_pandas()
                assert isinstance(df, pd.DataFrame)
                md = df.to_markdown()
                assert md.strip(), "Rendered markdown is empty"
                tables.append(md)
                print(md)

        assert tables, "No tables were extracted from the tutorial document"
        assert expected_markdown == tables[0].strip(), "Extracted table does not match expected markdown snapshot"
