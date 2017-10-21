import systemcheck
from systemcheck import checks
from systemcheck import models
import logging
import yaml
from pprint import pprint, pformat
logger=logging.getLogger('systemcheck.checks.utils')

def exportChecks(filename, session, format='yaml', saObject=None):
    """ Export Checks to File

    :param filename: The name of the export file
    :param format: The export format (possbible Values: yaml, xml, json)
    :param saObject: The object from which the export should start. If None, then the entire tree is getting exported.



    """

    if saObject is None:
        saObject=session.query(systemcheck.checks.models.Check).filter_by(name='RootNode').one()

    with open(filename, 'w') as fh:
        if format=='yaml':
            yamltext=saObject.to_yaml()
            fh.write(yamltext)
        elif format=='json':
            fh.write(saObject.to_json())

    return systemcheck.utils.Result(message='Export Successful')

def readChecksYaml(filename):
    """ Read Checks in YAML format

    :param filename: The yaml file that contains the check definitions
    """

    with open(filename, 'r') as fh:
        try:
            data=yaml.load(fh)
        except yaml.YAMLError as err:
            pprint(err.args)

    return data

def buildSaObject(data, saClass=None):
    logger.debug('building sqlalchemy object from data: %s')
    type = data.get('type')

    params=dict()

    if saClass is None:
        saClass=systemcheck.checks.models.Check

    parentClassName=data.get('type')


    for key, value in data.items():
        if not isinstance(value, list):
            params[key] = value

    saObject=saClass(**params)
    for key, value in data.items():
        if isinstance(value, list):
#            extendedList = getattr(saObject, key)
            for subitem in value:
                newClassName=None
                if key=='params':
                    # Parameters do not inherit from the Checks tree, but are simple references. In this case, the name
                    # of the class is the parent's class name with '__params' as suffix.
                    newClassName=parentClassName+'__params'
                elif key=='restrictions':
                    # Similar to parameters, restrictions do not inherit from the Checks tree either. In this case, the name
                    # of the class is the parent's class name with '__restrictions' as suffix.
                    newClassName=parentClassName+'__restrictions'
                else:
                    newClassName = subitem.get('type')

                if newClassName is not None:
                    newClass = systemcheck.models.utils.get_class_by_name(models.meta.Base, newClassName)
                    newObject=buildSaObject(subitem, newClass)
                    if newObject is not None:
                        getattr(saObject, key).append(newObject)
                else:
                    logger.error('Class Name could notbe determined: %s', pformat(subitem))
    return saObject


def importChecks(filename, session=None, format='yaml'):
    """ Import Checks

    :param filename: Name of the file that should get imported
    :param session: The session that should be used for importing the export
    :param format: The of the file
    """
    logger.debug('Importing Checks from file %s', filename)
    data=readChecksYaml(filename)
    if session is None:
        session=systemcheck.session.SESSION
    node=buildSaObject(data)
    session.add(node)
    models.meta.base.Base.metadata.create_all(session.bind)
    session.commit()

    return node

if __name__ == '__main__':

    x = importChecks('../../tests/test_export.yaml')

    for child in x.children:
        print(child.name)
        for y in child.children:
            print(y.name)
            for z in y.children:
                print(z.name)
                for w in z.children:
                    pprint(w.params)