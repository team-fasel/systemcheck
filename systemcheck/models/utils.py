import sqlalchemy
from pprint import pformat
from systemcheck import models
from systemcheck import utils
from systemcheck.session import SESSION
import systemcheck
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import logging

def get_class_by_name(Base, class_name):

    return Base._decl_class_registry.get(class_name)

def is_relation(orm_object, attr_name):
    return hasattr(getattr(orm_object.__class__, attr_name).property, 'mapper')

def number_range_next_value(name, addName=True, session=SESSION):
    """ Return the next number range value


    :param NumberRangeName: The name of the number range
    :param addName: When set to True, the name of the number range will be added """

    logging.debug('getting next value for number range %s', name)


    number_range_object = session.query(models.NumberRange).filter_by(name=name.upper()).one()
    value=number_range_object.value
    if addName:
        logging.debug('Adding number range name')
        value = name+str(number_range_object.value)

    return value

def number_range_update_or_new(name, value, start=0, end=None, addName=True, session=systemcheck.session.SESSION):
    """ Create a new Number Range object

    :param name: Name of the Number Range Object
    :param value: value of the number range
    :param start: start value
    :param end: upper range value
    :param addName: Defines whether only the digit or the range name  and the digit should get returned """

    try:
        number_range_object = utils.get_or_create(session, models.NumberRange, name=name)
        number_range_object.value = value
        number_range_object.start = start
        number_range_object.end = end

        session.commit()
    except Exception as err:
        return utils.Fail(message='Creation of number range failed: {}'.format(pformat(err)))

    return utils.Result(data=number_range_object, message='Number Range Creation Succeeded')



if __name__ == '__main__':
    session=systemcheck.session.SESSION
    get_class_by_name(models.meta.Base)