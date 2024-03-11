from db_class import User, Book, Log

class Factory:
    def __init__(self, item_type=None):
        self.item_type = item_type
        self.type_map = {
            "user" : User,
            "book" : Book,
            "log"  : Log,
        }
    
    def create(self, data_dict=None, **kwargs):
        if data_dict is not None:
            kwargs.update(data_dict)
        return self.type_map[self.item_type](**kwargs)