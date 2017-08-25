import systemcheck
import os

#from systemcheck.systems.generic.models import GenericSystemTreeNode
#from systemcheck.systems.ABAP.models import SystemABAPFolder, SystemABAP, SystemABAPClient
#from systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries import CheckAbapCountTableEntries, CheckAbapCountTableEntries__params

dbconfig=dict(systemcheck.config.CONFIG['systems-db'])
dbpath=os.path.join(systemcheck.config.CONFIG['application']['absolute_path'], dbconfig['dbname'])
dbconfig['sqlalchemy.url']=r'{}'.format(dbconfig['sqlalchemy.url'].replace('{dbpath}', dbpath))

engine = systemcheck.models.meta.base.engine_from_config(dbconfig)

systemcheck.models.meta.base.Base.metadata.create_all(engine)

# The session is initialized with expire_on_commit to prevent problems with expired nodes in the QTreeAbstractItemModel
# after a commit.
session_factory = systemcheck.models.meta.base.sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)


SESSION = systemcheck.models.meta.base.scoped_session(session_factory)

