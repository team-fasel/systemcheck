# -*- coding: utf-8 -*-

""" Configuration

This file sets up the global configuration for the system check application


"""

# define authorship information
__authors__     = ['Lars Fasel']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2017'
__license__     = 'MIT'

# maintanence information
__maintainer__  = 'Lars Fasel'
__email__       = 'systemcheck@team-fasel.com'

from configparser import ConfigParser
from systemcheck.utils import get_absolute_systemcheck_path
from systemcheck import model
from systemcheck.systems.ABAP.model import AbapTreeNode
from systemcheck.model.meta.base import scoped_session, sessionmaker, engine_from_config

import os


CONFIG = ConfigParser()
path_to_settings=os.path.join(get_absolute_systemcheck_path(), 'settings.ini')

CONFIG.read(path_to_settings)
CONFIG['application']['absolute_path']=get_absolute_systemcheck_path()

dbconfig=dict(CONFIG['systems-db'])
dbpath=os.path.join(CONFIG['application']['absolute_path'], dbconfig['dbname'])
dbconfig['sqlalchemy.url']=r'{}'.format(dbconfig['sqlalchemy.url'].replace('{dbpath}', dbpath))

engine = engine_from_config(dbconfig)
model.meta.base.Base.metadata.create_all(engine)

# The session is initialized with expire_on_commit to prevent problems with expired nodes in the QTreeAbstractItemModel
# after a commit.
session_factory = sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)


SESSION = scoped_session(session_factory)

if SESSION.query(AbapTreeNode).filter(AbapTreeNode.type== 'ROOT').count() == 0:
    SESSION.add(AbapTreeNode(type='ROOT', name='RootNode'))
    SESSION.commit()


