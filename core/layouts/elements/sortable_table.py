"""
This module implements a sortable table by using the table implemented in `PySimpleGUI`.
"""


from FreeSimpleGUI import Table



class SortableTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sort_column = None
        self._sort_reverse = False

    def sort_by_column(self, column: int):
        if self.Values is None or not self.Values:
            return

        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        def try_parse(val: str|int|float):
            try:
                return float(val) if val not in [None, ""] else float('nan')
            except ValueError:
                return str(val).lower() if isinstance(val, str) else val

        sorted_data = sorted(self.Values, key=lambda x: try_parse(x[column]), reverse=self._sort_reverse)
        self.update(values=sorted_data)