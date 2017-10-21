import sqlalchemy
from pprint import pprint
from systemcheck import models
import systemcheck


def get_class_by_name(Base, class_name):

    return Base._decl_class_registry.get(class_name)


if __name__ == '__main__':
    session=systemcheck.session.SESSION

    pprint(models.meta.Base)

    get_class_by_name(models.meta.Base)