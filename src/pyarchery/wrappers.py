import tempfile
from typing import Any, Iterator, List, Optional

import pyarrow as pa

from .archery import (
    Cell as JCell,
)
from .archery import (
    Document as JDocument,
)
from .archery import (
    Header as JHeader,
)
from .archery import (
    Row as JRow,
)
from .archery import (
    Sheet as JSheet,
)
from .archery import (
    Table as JTable,
)
from .archery import (
    TableGraph as JTableGraph,
)


class CellWrapper:
    """Wrapper for the Java Cell class, providing a Pythonic interface."""

    def __init__(self, cell: JCell):
        """Initialize the CellWrapper.

        Args:
            cell (JCell): The Java Cell instance.

        """
        self._cell = cell

    @property
    def value(self) -> str:
        """Get the value of the cell.

        Returns:
            str: The value of the cell.

        """
        return str(self._cell.getValue())

    def __repr__(self) -> str:
        """Return a string representation of the cell.

        Returns:
            str: The string representation.

        """
        return f"Cell(value={self.value})"


class RowWrapper:
    """Wrapper for the Java Row class, providing a Pythonic interface."""

    def __init__(self, row: JRow):
        """Initialize the RowWrapper.

        Args:
            row (JRow): The Java Row instance.

        """
        self._row = row

    @property
    def cells(self) -> List[CellWrapper]:
        """Get the list of cells in the row.

        Returns:
            List[CellWrapper]: A list of CellWrapper instances.

        """
        return [CellWrapper(cell) for cell in self._row.cells()]

    def __iter__(self) -> Iterator[CellWrapper]:
        """Iterate over the cells in the row.

        Returns:
            Iterator[CellWrapper]: An iterator over the cells.

        """
        return iter(self.cells)


class HeaderWrapper:
    """Wrapper for the Java Header class, providing a Pythonic interface."""

    def __init__(self, header: JHeader):
        """Initialize the HeaderWrapper.

        Args:
            header (JHeader): The Java Header instance.

        """
        self._header = header

    @property
    def name(self) -> str:
        """Get the name of the header.

        Returns:
            str: The name of the header.

        """
        return str(self._header.getName())

    @property
    def tag_value(self) -> Optional[str]:
        """Get the tag value of the header.

        Returns:
            Optional[str]: The tag value if present, None otherwise.

        """
        tag = self._header.getTag()
        if tag and not tag.isUndefined():
            return tag.getValue()
        return None


try:
    import pandas as pd
except ImportError:
    pd = None


class TableWrapper:
    """Wrapper for the Java Table class, providing a Pythonic interface."""

    def __init__(self, table: JTable):
        """Initialize the TableWrapper.

        Args:
            table (JTable): The Java Table instance.

        """
        self._table = table

    @property
    def headers(self) -> List[HeaderWrapper]:
        """Get the list of headers in the table.

        Returns:
            List[HeaderWrapper]: A list of HeaderWrapper instances.

        """
        return [HeaderWrapper(h) for h in self._table.headers()]

    @property
    def rows(self) -> Iterator[RowWrapper]:
        """Iterate over the rows in the table.

        Returns:
            Iterator[RowWrapper]: An iterator over RowWrapper instances.

        """
        for row in self._table.rows():
            yield RowWrapper(row)

    @property
    def header_names(self) -> List[str]:
        """Get the list of header names.

        Returns:
            List[str]: A list of header names.

        """
        return [h.name for h in self.headers]

    def to_pydict(self) -> dict[str, List[Any]]:
        """Convert the table to a python dictionary of lists (column-oriented).

        Returns:
            dict[str, List[Any]]: A dictionary where keys are header names and values are lists of cell values.

        """
        data = {name: [] for name in self.header_names}
        headers = self.headers

        for row in self.rows:
            cells = row.cells
            # Handle potential mismatch in cell count vs header count
            # We assume cells align with headers by index
            for i, header in enumerate(headers):
                if i < len(cells):
                    data[header.name].append(cells[i].value)
                else:
                    data[header.name].append(None)
        return data

    def to_arrow(self) -> pa.Table:
        """Convert the table to a PyArrow Table.

        Returns:
            pa.Table: A PyArrow Table representation of the table.

        """
        with tempfile.NamedTemporaryFile() as temp:
            file_path = temp.name
            self._table.to_arrow(file_path)
            with pa.ipc.open_stream(file_path) as reader:
                return reader.read_all()

    def to_csv(self, path: str):
        """Write the table to a CSV file.

        Args:
            path (str): The path to write the CSV file to.

        """
        self._table.to_csv(path)

    def to_pandas(self):
        """Convert the table to a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame representation of the table.

        Raises:
            ImportError: If pandas is not installed.

        """
        if pd is None:
            raise ImportError("pandas is not installed. Please install it with 'pip install pyjarchery[pandas]'")
        return pd.DataFrame(self.to_pydict())


class SheetWrapper:
    """Wrapper for the Java Sheet class, providing a Pythonic interface."""

    def __init__(self, sheet: JSheet):
        """Initialize the SheetWrapper.

        Args:
            sheet (JSheet): The Java Sheet instance.

        """
        self._sheet = sheet

    @property
    def table(self) -> Optional[TableWrapper]:
        """Get the table from the sheet.

        Returns:
            Optional[TableWrapper]: The TableWrapper if a table is present, None otherwise.

        """
        opt_table = self._sheet.getTable()
        if opt_table.isPresent():
            return TableWrapper(opt_table.get())
        return None

    def get_table_graph(self) -> Optional[JTableGraph]:
        """Get the table graph from the sheet.

        Returns:
            Optional[JTableGraph]: The Java TableGraph if present, None otherwise.

        """
        opt_table_graph = self._sheet.getTableGraph()
        if opt_table_graph.isPresent():
            return opt_table_graph.get()
        return None

    def add_sheet_listener(self, listener: Any):
        """Add a sheet listener.

        Args:
            listener: The listener to add.

        """
        self._sheet.addSheetListener(listener)


class DocumentWrapper:
    """Wrapper for the Java Document class, providing a Pythonic interface."""

    def __init__(self, document: JDocument):
        """Initialize the DocumentWrapper.

        Args:
            document (JDocument): The Java Document instance.

        """
        self._document = document

    @property
    def sheets(self) -> Iterator[SheetWrapper]:
        """Iterate over the sheets in the document.

        Returns:
            Iterator[SheetWrapper]: An iterator over SheetWrapper instances.

        """
        for sheet in self._document.sheets():
            yield SheetWrapper(sheet)

    def __enter__(self) -> "DocumentWrapper":
        """Enter the context manager.

        Returns:
            DocumentWrapper: This DocumentWrapper instance.

        """
        self._document.__enter__()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]):
        """Exit the context manager.

        Args:
            exc_type: The type of the exception.
            exc_val: The value of the exception.
            exc_tb: The traceback of the exception.

        """
        self._document.__exit__(exc_type, exc_val, exc_tb)
