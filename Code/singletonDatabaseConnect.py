from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SingletonDatabaseConnect:
    def __new__(cls, db_url=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonDatabaseConnect, cls).__new__(cls)
            cls.instance.engine = create_engine(db_url)
            cls.instance.Session = sessionmaker(bind=cls.instance.engine)
        return cls.instance

    def get_session(self):
        return self.Session()
    
    def get_engine(self):
        return self.engine