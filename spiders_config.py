CONFIG = {
    "spiders": {
        "MicrosoftAcademicsSpider": {
            "page_limit": None,
            "citation_count_filter": 5,
            "timeout": 10,
            "max_queries": 10,
            "headless": [True, True],
            "depth_limit": 0,
            "pub_year_filter": 2005,
            "sub_page_citation_limit": 500,
            "follow_recommendations": False,
            "csv_path": "./notebooks/data"
        },
    }
}
