CONFIG = {
    "spiders": {
        "MicrosoftAcademicsSpider": {
            "page_limit": 2,
            "citation_count_filter": 5,
            "timeout": 10,
            "max_queries": 2,
            "headless": [False, True],
            "pub_year_filter": 2005,
            "csv_path": "csv_exports",
            "nb_keywords": 3,
            "keyword_file": "keywords_en.csv"
        },
    }
}
