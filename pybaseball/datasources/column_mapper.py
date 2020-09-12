

class GenericColumnMapper:

    def __init__(self):
        self.call_counts = {}

    def _short_circuit(self, column_name):
        return ""

    def map_list(self, column_names):
        self.call_counts = {}
        for column_name in column_names:
            yield self.map(column_name)

    def map(self, column_name: str) -> str:
        self.call_counts[column_name] = self.call_counts.get(column_name, 0) + 1
        # First time around use the actual column name
        if self.call_counts[column_name] == 1:
            return column_name

        munged_value = self._short_circuit(column_name)
        # Just tack on a number for other calls
        return munged_value if munged_value else column_name + " " + str(self.call_counts[column_name])


class BattingStatsColumnMapper(GenericColumnMapper):
    def _short_circuit(self, column_name):
        # Rename the second FB% column
        if column_name == "FB%" and self.call_counts[column_name] == 2:
            return "FB% (Pitch)"
