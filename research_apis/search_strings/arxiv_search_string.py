from research_apis.search_strings.base_search_string import BaseSearchString


class ArXivSearchString(BaseSearchString):

    API_URL = 'http://export.arxiv.org/api/query?search_query='

    def __init__(self, paper_limit: int = 10):
        super().__init__()
        self.paper_limit = paper_limit

    def generate_search_string(self):
        if self.name:
            raise ValueError('Search string is already set, cannot override.')
        self.name = "+AND+".join([
            '(' + '+OR+'.join([
                ArXivSearchString.map_keyword_to_title_and_abstract(y)
                for y in x
            ]) + ')'
            for x in self._get_search_string_terms()
        ])

    def get_query_from_search_string(self):
        if not self.name:
            self.generate_search_string()
        query = self.API_URL + self.name
        if self.paper_limit:
            query += f'&max_results={self.paper_limit}'
        return query.replace('(', '%28').replace(')', '%29')

    @classmethod
    def get_sample_ss(cls):
        inst = cls()
        inst.name = ArXivSearchString.map_keyword_to_title_and_abstract('carbon credits') + '+AND+' + \
            ArXivSearchString.map_keyword_to_title_and_abstract('carbon markets')
        return inst

    @staticmethod
    def map_keyword_to_title_and_abstract(s: str) -> str:
        return f"all:{s.replace(' ', '+')}"

    def clear(self):
        self.name = None
        self.system_kw = None
        self.intervention_kw = None
        self.outcome_kw = None

    def JSON(self) -> dict:
        return super().JSON()
