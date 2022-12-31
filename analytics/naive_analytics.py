import requests
from notion.resource import NotionComponentType, NotionComponent


class NotionNaiveAnalytics:
    def __init__(self, worker, token=''):
        self.worker = worker
        self.token = token
        self.nb_worker_calls = 0

    def worker_call(self, suffix_url):
        url = f'{self.worker}{suffix_url}'
        self.nb_worker_calls += 1
        return requests.get(url, headers={'Authorization': f'Bearer {self.token}'}).json()

    def analytics(self, root_page_id):
        def get_page_component(page_id):
            cur_component = NotionComponent(page_id, comp_type=NotionComponentType.PAGE)

            # call to notion worker
            res = self.worker_call(f'/page/{page_id}/')

            # parse subpages
            try:
                if res[page_id]["value"]["type"] != NotionComponentType.PAGE.value:
                    return cur_component

                if "content" not in res[page_id]["value"]:
                    return cur_component

                sub_pages = res[page_id]["value"]["content"]
                for sub_page_id in sub_pages:
                    if res[sub_page_id]["value"]["type"] == NotionComponentType.PAGE.value:
                        sub_component = get_page_component(sub_page_id)
                        cur_component.attach_child(sub_component)

                    elif res[sub_page_id]["value"]["type"] == NotionComponentType.DATABASE.value:
                        sub_component = NotionComponent(sub_page_id, comp_type=NotionComponentType.DATABASE)

                        # get all non-empty pages inside a database
                        for database_sub_page in res[sub_page_id]["collection"]["data"]:
                            database_sub_component = get_page_component(database_sub_page["id"])
                            sub_component.attach_child(database_sub_component)

                        cur_component.attach_child(sub_component)
            except Exception as e:
                print(f"page_id: {page_id}: error: {e}")
                return cur_component

            return cur_component

        root_page = get_page_component(root_page_id)
        return root_page
