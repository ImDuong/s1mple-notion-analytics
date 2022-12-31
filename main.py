from dotenv import load_dotenv
import os
import time
from analytics.naive_analytics import NotionNaiveAnalytics

if __name__ == '__main__':
    # init
    # root_page is required to have the dash signs.
    root_page_id = 'f7c1ad03-71b6-43e7-a569-a41f8ac0599b'
    load_dotenv()
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_WORKER = os.getenv('NOTION_WORKER')

    nna = NotionNaiveAnalytics(NOTION_WORKER, token=NOTION_TOKEN)

    start_time = time.time()
    root_page = nna.analytics(root_page_id)
    end_time = time.time() - start_time

    print("-------Analytics Result-------")
    print(f"{nna.nb_worker_calls} calls in {end_time} seconds")
    print(f"Number of pages: {root_page.nb_pages + 1}")  # plus 1 for the root page
    print(f"Number of databases: {root_page.nb_databases}")
