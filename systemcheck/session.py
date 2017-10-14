import systemcheck
from marshmallow_sqlalchemy import ModelConversionError, ModelSchema
import os
from systemcheck import models
from systemcheck.config import CONFIG


def setup_schema(Base, session):
    # Create a function which incorporates the Base and session information
    def setup_schema_fn():
        for class_ in Base._decl_class_registry.values():
            if hasattr(class_, '__tablename__'):
                if class_.__name__.endswith('Schema'):
                    raise ModelConversionError(
                        "For safety, setup_schema can not be used when a"
                        "Model class ends with 'Schema'"
                    )

                class Meta(object):
                    model = class_
                    sqla_session = session

                schema_class_name = '%sSchema' % class_.__name__

                schema_class = type(
                    schema_class_name,
                    (ModelSchema,),
                    {'Meta': Meta}
                )

                setattr(class_, '__marshmallow__', schema_class)

    return setup_schema_fn

dbconfig=dict(CONFIG['systems-db'])
dbpath=os.path.join(CONFIG['application']['absolute_path'], dbconfig['dbname'])
dbconfig['sqlalchemy.url']=r'{}'.format(dbconfig['sqlalchemy.url'].replace('{dbpath}', dbpath))
# The session is initialized with expire_on_commit to prevent problems with expired nodes in the QTreeAbstractItemModel
# after a commit.
engine = models.meta.base.engine_from_config(dbconfig)
session_factory = models.meta.base.sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)
SESSION = models.meta.base.scoped_session(session_factory)

models.meta.event.listen(models.meta.mapper, 'after_configured', setup_schema(models.meta.Base, SESSION))
models.meta.base.Base.metadata.create_all(engine)


