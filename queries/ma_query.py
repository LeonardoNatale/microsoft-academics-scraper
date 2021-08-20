from typing import List


class MAQuery:

    def __init__(self, query: List, columns: List):
        """
        @param query: A list of the keywords of the query
        @param columns: the columns of the file from which the keywords are from.
        """
        self.query = query
        self.columns = columns

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, value):
        self.__query = value

    @property
    def columns(self):
        return self.__columns

    @columns.setter
    def columns(self, value):
        self.__columns = value

    def query_as_string(self):
        """
        returns the query as a string joined by spaces.
        """
        return " ".join(self.query)

    def __str__(self):
        return ', '.join([f"{lst[0]} ({lst[1]})" for lst in list(zip(self.query, self.columns))])
