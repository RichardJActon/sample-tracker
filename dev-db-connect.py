# invoke from src/sample_tracker with:
# exec(open("../../dev-db-connect.py").read())

# for easy module reloading while working
from importlib import reload
# e.g. 
# reload(datamodel)
# to reload imports from the datamodel module whilst working

import yaml
from pymongo import MongoClient
from typing import Any
import os
from odmantic import SyncEngine

with open("../../config.yaml","r") as f:
    conf = yaml.safe_load(f)

conf["MONGO"]["PWD"] = os.environ["APP_MONGO__PWD"]

def odmantic_sync_engine(conf: dict[str, Any]) -> SyncEngine:
    """
    Create an Odmantic engine object to interface with the MongoDB istance
    with the details provided in the application config
    """
    client: MongoClient[dict[str, Any]] = MongoClient(
        host = conf['HOST'],
        port = conf['PORT'],
        username = conf['USER'],
        password = conf['PWD'],
        authSource = conf['AUTH_SOURCE']
    )

    engine = SyncEngine(client = client, database = conf["DATABASE"])
    return engine

engine = odmantic_sync_engine(conf["MONGO"])
