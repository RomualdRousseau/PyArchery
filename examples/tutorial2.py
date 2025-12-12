import pyarchery

REPO_BASE_URL = "https://raw.githubusercontent.com/RomualdRousseau/Archery/main/archery-models"
MODEL_NAME = "sales-english"
FILE_PATH = "examples/data/document with multiple tables.xlsx"
FILE_ENCODING = "UTF-8"


def get_model():
    builder = pyarchery.model_from_url(f"{REPO_BASE_URL}/{MODEL_NAME}/{MODEL_NAME}.json")

    entities = [v for v in builder.getEntityList() if v != "PACKAGE"]
    entities.append("PRODUCTNAME")

    patterns = {k: v for (k, v) in builder.getPatternMap().items() if v != "PACKAGE"}
    patterns["\\D+\\dml"] = "PRODUCTNAME"

    parser = pyarchery.LayexTableParser(["(v.$)+"], ["(()(S+$))(()([/^TOTAL/|v].+$)())+(/TOTAL/.+$)"])

    return builder.setEntityList(entities).setPatternMap(patterns).setTableParser(parser).build()


def main():
    with pyarchery.load(
        FILE_PATH,
        encoding=FILE_ENCODING,
        model=get_model(),
        hints=[pyarchery.INTELLI_LAYOUT, pyarchery.INTELLI_TIME],
        recipe=["sheet.setCapillarityThreshold(0)"],
        tag_case="SNAKE",
    ) as doc:
        for sheet in doc.sheets:
            table = sheet.table
            if table:
                print(table.to_pandas().to_markdown())


if __name__ == "__main__":
    main()
