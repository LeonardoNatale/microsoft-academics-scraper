from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd
from models.db_session import DBSession
from time import time


class BaseCSVDataFrame:

    def __init__(self, data: pd.DataFrame = None):
        self.data = data

    @property
    @abstractmethod
    def REQUIRED_COLUMNS(self) -> list:
        pass

    def data_integrity_check(self) -> bool:
        """
        Check that all the columns that need to be inserted into the DB are present in the DataFrame.
        :return: True if the check is passed, raises otherwise.
        """
        if all([col in self.data.columns for col in self.REQUIRED_COLUMNS]):
            return True
        else:
            raise ValueError(
                f'Columns of the DataFrame should at least include the following columns :\n{self.REQUIRED_COLUMNS}.\n'
                f' DataFrame columns :\n{list(list(self.data.columns))}'
            )

    def nan_to_none(self) -> None:
        """
        Transforms the NaN and NaT values to None
        """
        self.data = self.data.replace({
            np.nan: None,
            pd.NaT: None
        })

    def insert_df(self, session: DBSession, limit: int = None) -> int:
        """
        Inserts an entire DataFrame to the project DB.

        :param session: The DB session.
        :param limit: The limit in the number of rows to insert.
        """
        start = time()
        self.data_integrity_check()
        self.nan_to_none()
        if limit:
            self.data = self.data.head(limit)
        session.logger.info(f'Inserting data of shape {self.data.shape}.')
        insertion_status = pd.DataFrame(
            self.data.apply(func=self.insert_to_db, axis=1, session=session).tolist(),
            columns=['added', 'duplicate']
        )
        session.session.commit()
        duplicates = list(insertion_status.duplicate[~insertion_status.duplicate.isna()])
        insert_count = insertion_status.added.sum()
        end = time()
        output_info = f'{insert_count} rows were actually inserted.\n'
        ld = len(duplicates)
        if ld:
            dup_str = '\n - '.join([''] + duplicates)
            output_info += f'The following ({ld}) elements were not added because they were duplicates :{dup_str}\n'
        output_info += f'Elapsed : {round(end - start, 2)}s'
        session.logger.info(output_info)
        return insert_count

    @abstractmethod
    def insert_to_db(self, row: pd.Series, session: DBSession) -> None:
        """
        Inserts a row to the project DataBase

        :param row: The row to insert.
        :param session: The database session.
        """
        pass

    def truncate_old_data(self, column, value) -> None:
        """
        Truncates the old data.

        :param column: The datetime column
        :param value: The threshold value.
        """
        self.data = self.data[self.data[column] > value]

    def columns_to_date(self, columns: List[str]) -> None:
        """
        Converts the given columns of the DataFrame to datetime format.

        :param columns: The columns to convert to date.
        :return:
        """
        for col in columns:
            self.data[col] = pd.to_datetime(self.data[col])

    @abstractmethod
    def row_to_dict(self, row: pd.Series) -> dict:
        """
        Converts a pandas row to a dictionary.
        :param row: the pandas row
        :return: The row as a dict.
        """
        pass

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value
