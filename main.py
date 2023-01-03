import sys

from dotenv import dotenv_values, load_dotenv
import os
import time
from analytics.naive_analytics import NotionNaiveAnalytics
from analytics.threading_analytics import NotionThreadingAnalytics


def init():
    load_dotenv()
    run_mode = os.getenv("RUN_MODE")

    if run_mode == "prod":
        env_file = ".env.prod"
    elif run_mode == "local":
        env_file = ".env.local"
    else:
        env_file = ".env"

    return {
        **dotenv_values(env_file)
    }


if __name__ == '__main__':
    # init config
    config = init()

    # root_page is required to have the dash signs.
    root_page_id = 'd584ee7d-5fd9-48a5-9dc4-cf90246b056a'

    nna = NotionNaiveAnalytics(config["NOTION_WORKER"], token=config["NOTION_TOKEN"])
    # nna = NotionThreadingAnalytics(config["NOTION_WORKER"], token=config["NOTION_TOKEN"])

    start_time = time.time()
    root_page = nna.analytics(root_page_id)
    end_time = time.time() - start_time

    print("-------Analytics Result-------")
    print(f"{nna.nb_worker_calls} calls in {end_time} seconds")
    print(f"Number of pages: {root_page.nb_pages + 1}")  # plus 1 for the root page
    print(f"Number of databases: {root_page.nb_databases}")
