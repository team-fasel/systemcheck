from systemcheck import models
from systemcheck.systems.ABAP.models import AbapTreeNode
from systemcheck.models.meta.base import scoped_session, sessionmaker, engine_from_config
from systemcheck.config import CONFIG
import os

dbconfig=dict(CONFIG['systems-db'])
dbpath=os.path.join(CONFIG['application']['absolute_path'], dbconfig['dbname'])
dbconfig['sqlalchemy.url']=r'{}'.format(dbconfig['sqlalchemy.url'].replace('{dbpath}', dbpath))

engine = engine_from_config(dbconfig)
models.meta.base.Base.metadata.create_all(engine)

# The session is initialized with expire_on_commit to prevent problems with expired nodes in the QTreeAbstractItemModel
# after a commit.
session_factory = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)


SESSION = scoped_session(session_factory)

if SESSION.query(AbapTreeNode).filter(AbapTreeNode.parent_id==None).count() == 0:
    SESSION.add(AbapTreeNode(type='FOLDER', name='RootNode'))
    SESSION.commit()
