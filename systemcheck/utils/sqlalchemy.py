import systemcheck
from systemcheck.systems.ABAP.models import *
def get_or_create(session, model, **kwargs):
    """ Get or create a SQLAlchemy Object

    :param session: The SQLAlchemy Session that should be used
    :param model: The SQLAlchemy Model that we are looking for
    :param kwargs: The model attributes

    """
    systemcheck.models.meta.base.Base.metadata.create_all(systemcheck.session.engine)
    instance = session.query(model).filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()


    return instance
