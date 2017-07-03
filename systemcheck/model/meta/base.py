from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config, MetaData
from decorator import decorator
from .schema import References

engine = None

def setup(config):
    """Setup the application given a config dictionary."""

    global engine
    engine = engine_from_config(config)
    Session.configure(bind=engine)
    return engine, Session

@decorator
def commit_on_success(fn, *arg, **kw):
    """Decorate any function to commit the session on success, rollback in
    the case of error."""

    try:
        result = fn(*arg, **kw)
        Session.commit()
    except:
        Session.rollback()
        raise
    else:
        return result

# bind the Session to the current request
# Convention within Pyramid is to use the ZopeSQLAlchemy extension here,
# allowing integration into Pyramid's transactional scope.
Session = sessionmaker(bind=engine)

class Base(References):
    pass

Base = declarative_base(cls=Base)

# establish a constraint naming convention.
# see http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions
#
Base.metadata.naming_convention={
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}

class CheckBase(References):
    pass

CheckBase = declarative_base(cls=CheckBase)

# establish a constraint naming convention.
# see http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions
#

CheckBase.metadata.naming_convention={
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}