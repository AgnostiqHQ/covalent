"""DB Config"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from covalent_dispatcher._db.dispatchdb import DispatchDB

# dispatch_db = DispatchDB()
# SQLALCHEMY_DATABASE_URL = dispatch_db._get_data_store()
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
engine = DispatchDB()._get_data_store(initialize_db=True).engine
Base = declarative_base()
