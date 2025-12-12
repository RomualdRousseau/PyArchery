import pyarchery

FILE_PATHS = [
    "examples/data/document with simple table.csv",
    "examples/data/document with simple table.xls",
    "examples/data/document with simple table.xlsx",
]


def main():
    for file_path in FILE_PATHS:
        with pyarchery.load(file_path) as doc:
            for sheet in doc.sheets:
                table = sheet.table
                if table:
                    for header in table.headers:
                        print(header.tag_value, end=" ")
                    print()
                    for row in table.rows:
                        for cell in row.cells:
                            print(cell.value, end=" ")
                        print()


if __name__ == "__main__":
    main()
