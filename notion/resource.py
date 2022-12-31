from enum import Enum


class NotionComponentType(Enum):
    UNKNOWN = 'unknown'
    PAGE = 'page'
    DATABASE = 'collection_view'


class NotionComponent:
    def __init__(self, comp_id, comp_type=NotionComponentType.UNKNOWN):
        self.id = comp_id
        self.type = comp_type
        self.title = ""
        self.children = {}
        self.nb_pages = 0
        self.nb_databases = 0

    def attach_child(self, child):
        if not isinstance(child, NotionComponent):
            raise TypeError

        # assign child
        self.children[child.id] = child

        # accumulate nb_pages
        self.nb_pages += child.nb_pages

        # accumulate nb_databases
        self.nb_databases += child.nb_databases

        # accumulate for the child
        if child.type == NotionComponentType.PAGE:
            self.nb_pages += 1

        if child.type == NotionComponentType.DATABASE:
            self.nb_databases += 1
