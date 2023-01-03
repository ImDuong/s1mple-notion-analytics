from multiprocessing.pool import ThreadPool
import requests
from notion.resource import NotionComponentType, NotionComponent
from ratelimiter import RateLimiter

NB_WORKERS = 12


class NotionThreadingAnalytics:
    def __init__(self, worker, token=''):
        self.worker = worker
        self.token = token
        self.nb_worker_calls = 0

    # the number of calls really depends on how notion api worker work with notion api
    # as data taken in 1/1/2023, notion api's rate limit is an average of 3 requests in 1 second
    @RateLimiter(max_calls=2, period=1)
    def call_worker(self, suffix_url):
        url = f'{self.worker}{suffix_url}'
        self.nb_worker_calls += 1

        response = {}
        raw_response = ""
        while len(response) == 0:
            try:
                raw_response = requests.get(url, headers={'Authorization': f'Bearer {self.token}'})
                response = raw_response.json()
                break
            except Exception as e:
                print(f"error {e} when calling to {url}")
                print(f"raw response: {raw_response}")

        return response

    def analytics(self, root_page_id):
        pool = ThreadPool(processes=NB_WORKERS)

        def get_page_component(page_id):
            cur_component = NotionComponent(page_id)

            # call to notion worker
            response = self.call_worker(f'/page/{page_id}/')

            if page_id not in response:
                print(f"page_id: {page_id}: error: empty response")
                return cur_component

            # parse subpages
            try:
                if response[page_id]["value"]["type"] != NotionComponentType.PAGE.value:
                    return cur_component

                # set page type to current component
                cur_component.type = NotionComponentType.PAGE
                # cur_component.title = response[page_id]["value"]["properties"]["title"][0][0]

                if "content" not in response[page_id]["value"]:
                    return cur_component

                sub_page_ids = response[page_id]["value"]["content"]
                for sub_page_id in sub_page_ids:
                    sub_component = NotionComponent(sub_page_id)
                    if response[sub_page_id]["value"]["type"] == NotionComponentType.PAGE.value:
                        sub_component.type = NotionComponentType.PAGE
                        # sub_component.title = response[sub_page_id]["value"]["properties"]["title"][0][0]

                        # find sub-components of this sub-component directly to reduce the number of calls
                        # (this method works only when notion worker supports one more layer)
                        if "content" in response[sub_page_id]["value"]:
                            sub_sub_page_ids = response[sub_page_id]["value"]["content"]
                            for sub_sub_component in pool.map(get_page_component, sub_sub_page_ids):
                                sub_component.attach_child(sub_sub_component)

                    elif response[sub_page_id]["value"]["type"] == NotionComponentType.DATABASE.value:
                        sub_component.type = NotionComponentType.DATABASE

                        # get all non-empty pages inside a database
                        database_sub_page_ids = [x["id"] for x in response[sub_page_id]["collection"]["data"]]
                        for database_sub_component in pool.map(get_page_component, database_sub_page_ids):
                            sub_component.attach_child(database_sub_component)

                    cur_component.attach_child(sub_component)

            except Exception as e:
                print(f">>> page_id: {page_id}: error: {e}")
                print(f"response: {response[page_id]['value']['content']}")
                return cur_component

            return cur_component

        root_page = get_page_component(root_page_id)

        pool.close()
        return root_page
