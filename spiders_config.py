CONFIG = {
    "spiders": {
        "MicrosoftAcademicsSpider": {
            "page_limit": 2,
            "citation_count_filter": 5,
            "timeout": 10,
            "max_queries": 2,
            "headless": [False, True],
            "depth_limit": 0,
            "pub_year_filter": 2005,
            "sub_page_citation_limit": 500,
            "follow_recommendations": False,
            "csv_path": "csv_exports",
            "keyword_file": "keywords_en.csv"
        },
    }
}
