import requests
import os
from dotenv import load_dotenv


def get_content(page_id, notion_worker, notion_token):
    # call to notion worker
    url = f'{notion_worker}/page/{page_id}/'
    r = requests.get(url, headers={'Authorization': f'Bearer {notion_token}'}).json()

    nb_pages = 1

    # parse subpages
    try:
        if r[page_id]["value"]["type"] != "page":
            return {page_id: 0}

        sub_pages = r[page_id]["value"]["content"]
        for sp in sub_pages:
            if r[sp]["value"]["type"] == "page":
                nb_pages += get_content(sp, notion_worker, notion_token)[sp]
    except Exception as e:
        print(f"page_id: {page_id}: error: {e}")
        return {page_id: 0}

    return {page_id: nb_pages}


if __name__ == '__main__':
    # init
    # root_page is required to have the dash signs.
    root_page = 'f7c1ad03-71b6-43e7-a569-a41f8ac0599b'
    load_dotenv()
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_WORKER = os.getenv('NOTION_WORKER')

    x = get_content(root_page, NOTION_WORKER, NOTION_TOKEN)
    print("------------")
    print("Result")
    print(x)
