class MAQuery:

    def __init__(self, query: str, is_project_oriented: bool = False):
        self.query = query
        self.is_project_oriented = is_project_oriented

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, value):
        self.__query = value

    @property
    def is_project_oriented(self):
        return self.__is_project_oriented

    @is_project_oriented.setter
    def is_project_oriented(self, value):
        self.__is_project_oriented = value

    def __str__(self):
        return self.query + ' -' + ((' ' if self.is_project_oriented else ' Not ') + f'project oriented').capitalize()
