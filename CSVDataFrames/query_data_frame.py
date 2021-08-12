from CSVDataFrames.base_csv_data_frame import BaseCSVDataFrame
import pandas as pd
from models.db_session import DBSession


class QueryDataFrame(BaseCSVDataFrame):

    REQUIRED_COLUMNS = [
        "title", "authors", "date", "abstract", "source", "DOI", "url", "query",
    ]

    def __init__(self, data: pd.DataFrame = None, database: str = ''):
        super().__init__(data=data)
        self.database_name = database

    @property
    def database_name(self) -> str:
        return self.__database_name

    @database_name.setter
    def database_name(self, value):
        self.__database_name = value

    def insert_to_db(self, row: pd.Series, session: DBSession):
        return session.insert_to_papers_db(content=self.row_to_dict(row))

    def row_to_dict(self, row: pd.Series) -> dict:
        return {
            **row.to_dict(),
            'registry': self.database_name
        }

