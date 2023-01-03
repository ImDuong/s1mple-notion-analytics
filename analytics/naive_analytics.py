import requests
from notion.resource import NotionComponentType, NotionComponent
from ratelimiter import RateLimiter
import time


MAX_NB_RETRIES = 10


class NotionNaiveAnalytics:
    def __init__(self, worker, token=''):
        self.worker = worker
        self.token = token
        self.nb_worker_calls = 0

    @RateLimiter(max_calls=2, period=1)
    def call_worker(self, suffix_url):
        url = f'{self.worker}{suffix_url}'
        self.nb_worker_calls += 1

        response = {}
        raw_response = ""
        nb_retries = 0
        while len(response) == 0 or nb_retries <= MAX_NB_RETRIES:
            try:
                raw_response = requests.get(url, headers={'Authorization': f'Bearer {self.token}'})
                response = raw_response.json()
                break
            except Exception as e:
                print(f"error {e} when calling to {url}")
                print(f"raw response: {raw_response}")

            nb_retries += 1
            time.sleep(10)

        return response

    def analytics(self, root_page_id):
        def get_page_component(page_id):
            cur_component = NotionComponent(page_id)

            # call to notion worker
            res = self.call_worker(f'/page/{page_id}/')

            if page_id not in res:
                print(f"page_id: {page_id}: error: empty response")
                return cur_component

            # parse subpages
            try:
                if res[page_id]["value"]["type"] != NotionComponentType.PAGE.value:
                    return cur_component

                # set page type to current component
                cur_component.type = NotionComponentType.PAGE
                # cur_component.title = res[page_id]["value"]["properties"]["title"][0][0]

                if "content" not in res[page_id]["value"]:
                    return cur_component

                sub_page_ids = res[page_id]["value"]["content"]
                for sub_page_id in sub_page_ids:
                    sub_component = NotionComponent(sub_page_id)
                    if res[sub_page_id]["value"]["type"] == NotionComponentType.PAGE.value:
                        sub_component.type = NotionComponentType.PAGE
                        # sub_component.title = res[sub_page_id]["value"]["properties"]["title"][0][0]

                        # find sub-components of this sub-component directly to reduce the number of calls
                        # (this method works only when notion worker supports one more layer)
                        if "content" in res[sub_page_id]["value"]:
                            sub_sub_page_ids = res[sub_page_id]["value"]["content"]
                            for sub_sub_page_id in sub_sub_page_ids:
                                sub_sub_component = get_page_component(sub_sub_page_id)
                                sub_component.attach_child(sub_sub_component)

                    elif res[sub_page_id]["value"]["type"] == NotionComponentType.DATABASE.value:
                        sub_component.type = NotionComponentType.DATABASE

                        # get all non-empty pages inside a database
                        for database_sub_page in res[sub_page_id]["collection"]["data"]:
                            database_sub_component = get_page_component(database_sub_page["id"])
                            sub_component.attach_child(database_sub_component)

                    cur_component.attach_child(sub_component)
            except Exception as e:
                print(f">>> page_id: {page_id}: error: {e}")
                print(f"response: {res[page_id]['value']['content']}")
                return cur_component

            return cur_component

        root_page = get_page_component(root_page_id)
        return root_page
