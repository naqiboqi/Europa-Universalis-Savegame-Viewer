"""
This module implements a sortable table by using the table implemented in `PySimpleGUI`.
"""


from FreeSimpleGUI import Table



class SortableTable(Table):
    """A subclass of PySimpleGUI's Table that supports sorting by columns.
    It enables sorting in ascending or descending order when a column is clicked.

    Attributes:
        _sort_column (int): The index of the currently sorted column.
        _sort_reverse (bool): A flag indicating whether the sort order is reversed.
    """
    def __init__(self, *args, **kwargs):
        """Initializes the SortableTable with the given arguments and keyword arguments.

        Args:
            *args: Variable length argument list for the Table constructor.
            **kwargs: Arbitrary keyword arguments for the Table constructor.
        """
        super().__init__(*args, **kwargs)
        self._sort_column = None
        self._sort_reverse = False

    def sort_by_column(self, column: int):
        """Sorts the table by the specified column index. Toggles the sort order
        between ascending and descending each time the same column is clicked.

        Args:
            column (int): The index of the column to sort by.
        """
        if self.Values is None or not self.Values:
            return

        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        def try_parse(val: str|int|float):
            """Attempts to convert the value to a float if possible, otherwise,
            returns the string version of the value.
            """
            try:
                return float(val) if val not in [None, ""] else float('nan')
            except ValueError:
                return str(val).lower() if isinstance(val, str) else val

        sorted_data = sorted(self.Values, key=lambda x: try_parse(x[column]), reverse=self._sort_reverse)
        self.update(values=sorted_data)
