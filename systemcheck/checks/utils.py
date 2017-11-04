import systemcheck
from systemcheck import checks
from systemcheck import models
import logging
import yaml
from systemcheck.utils import Result, Fail, get_absolute_systemcheck_path
import os
from os import listdir
from os.path import isfile, join


from pprint import pprint, pformat
logger=logging.getLogger('systemcheck.checks.utils')

def exportChecks(*args, folder=None, format='yaml', saObject=None, session=None, **kwargs):
    """ Export Checks to individual files

    :param filename: The name of the export file
    :param format: The export format (possbible Values: yaml, xml, json)
    :param saObject: The object from which the export should start. If None, then the entire tree is getting exported.
    :param session: The SQLAlchemy Session that should be used

    """

    status=dict(sucessful={}, failed={})

    if folder is None:
        folder = os.path.join(get_absolute_systemcheck_path(), 'checks', 'dump')

    if session is None:
        session = systemcheck.session.SESSION

    logger.info('Exporting Checks to Folder %s', folder)

    if saObject is None:
        logger.debug('No SQL Alchemy Object specified, exporting from Root')
        saObject=session.query(systemcheck.checks.models.Check).filter_by(name='RootNode').one()

    for child in saObject.children:
        result = exportChecks(session, folder=folder, format=format, saObject=child)

        if result.fail:
            return result

    if not saObject.type.upper().endswith('FOLDER') and saObject.parent_id is not None:
        logger.debug('Not a Folder Object, initiating export')

        #Build a safe filename
        temp="".join( x if (x.isalnum() or x in "._-") else '_' for x in saObject.name )
        filename='_'.join([saObject.type, temp])
        filename = filename +'.'+format
        logger.debug('determined filename: %s', filename)

        result = exportCheck(saObject=saObject, filename=os.path.join(folder, filename))
        if result.fail:
            status['failed'][saObject.name]=result.message
        else:
            status['sucessful'][saObject.name]=result.message


    return systemcheck.utils.Result(message='Export Successful', data=status)

def exportCheck(saObject, filename=None, session=None, format='yaml'):
    """ Export a single Check Object

    :param saObject: The SQLAlchemy Check Object
    :param filename: The name of the file to write the data into
    :param format: The output format
    :param session: The session that should be used.

    """

    # Build the path up to root node
    name = saObject.name

    treepath = []
    node = saObject.parent_node
    if node is not None:
        while node.parent_id is not None:
            treepath.insert(0, {'name': node.name, 'type': node.type, 'description': node.description})
            node = node.parent_node

    logger.debug('Determined Tree Path: %s', treepath)

    saObjectExportMetadata = dict()
    saObjectExportMetadata['filename'] = filename
    saObjectExportMetadata['treepath'] = treepath
    saObjectExportMetadata['object'] = saObject.to_dict()
    if format == 'yaml':
        try:
            yamltext = yaml.dump(saObjectExportMetadata)
        except Exception as err:
            logger.exception(err)
            return systemcheck.utils.Fail(message='Export Failed: {}'.format(pformat(err)))

    if filename:
        try:
            with open(os.path.join(filename), 'w') as fh:
                        fh.write(yamltext)
        except Exception as err:
            logger.exception(err)
            return systemcheck.utils.Fail(message='Export Failed: {}'.format(pformat(err)))

    return systemcheck.utils.Result(message='Export Successful', data=yamltext)


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

def buildSaObject(saData:dict, saClass=None):
    """ Build a SQLAlchemy Object from the retrieved dictionary


    :param saData: The dictionary representation of the Object
    :param saClass: a hint for the recursive processing to provide a correct class """

    logger.debug('building sqlalchemy object from data: %s')

    params=dict()

    if saClass is None:
        logger.debug('No Class Specified, determine class')
        saClassName=saData.get('type')
        saClass=models.get_class_by_name(models.meta.Base, saClassName)


    for key, value in saData.items():
        if not isinstance(value, list):
            # Lists are lists of other SQLAlchemy models. We need to ignore them when instantiating for the first time
            params[key] = value

    logger.debug('Parameter to instantiate SQLAlchemy Object: %s', pformat(params))

    try:
        saObject=saClass(**params)
    except Exception as err:
        logger.exception(err)
        return Fail(message='Error Building SQLAlchemy Object', data=err)

    for key, value in saData.items():
        if isinstance(value, list):
            logger.debug('%s is a list', key)
            for subitem in value:
                if key=='params':
                    # Parameters do not inherit from the Checks tree, but are simple references. In this case, the name
                    # of the class is the parent's class name with '__params' as suffix.
                    newClassName=saClassName+'__params'
                    logger.debug('Class name of key %s is %s', key, newClassName)
                elif key=='restrictions':
                    # Similar to parameters, restrictions do not inherit from the Checks tree either. In this case, the name
                    # of the class is the parent's class name with '__restrictions' as suffix.
                    newClassName=saClassName+'__restrictions'
                    logger.debug('Class name of key %s is %s', key, newClassName)
                else:
                    newClassName = subitem.get('type')

                if newClassName is not None:
                    newClass = systemcheck.models.utils.get_class_by_name(models.meta.Base, newClassName)

                    result = buildSaObject(subitem, newClass)
                    if result.fail:
                        return result

                    newObject=result.data
                    getattr(saObject, key).append(newObject)
                else:
                    logger.error('Class Name for attribute %s could notbe determined (%s)', key, pformat(subitem))

    return Result(message='SQLAlchem Object Built', data=saObject)

def importChecks(path=None, session=None):
    """ Import all Checks


    :param path: The path to the checks """
    logger.debug('Import Checks')

    success = dict()  #will be used for status tracking
    failed = dict() #will be used for status tracking

    if path is None:
        logger.debug('No path specified, using default path')
        path=get_absolute_systemcheck_path('checks/dump')

    logger.debug('Path: %s', path)


    checkFiles = [f
                  for f in listdir(path)
                  if isfile(join(path, f)) and f.endswith('.yaml')]

    logger.debug('idenfied files: %s', pformat(checkFiles))
    logger.debug('starting import:')
    for checkFile in checkFiles:
        logger.debug('  - %s', checkFile)

        result = importCheck(filename=join(path, checkFile), session=session)
        if result.fail:
            logger.error('Import of %s failed: %s', checkFile, result.message)
            failed[checkFile]=result.message
        else:
            logger.debug('Import of %s succeeded', checkFile)
            success[checkFile]=result.message

        if len(failed) > 0:
            message = 'Some imports failed!'
        else:
            message = 'Imports Succeeded'

        data = {'successful':success, 'failed':failed}

    return Result(message=message, data=data)

def importCheck(filename, session=None, format='yaml'):
    """ Import Checks

    :param filename: Name of the file that should get imported
    :param session: The session that should be used for importing the export
    :param format: The of the file
    """
    logger.debug('Importing Check from file %s', filename)

    try:
        data=readChecksYaml(filename)
    except Exception as err:
        return Fail(message='Error reading Checks file: {}'.format(pformat(err)))

    if session is None:
        session=systemcheck.session.SESSION

    try:
        result=buildSaObject(data['object'])
    except Exception as err:
        logger.exception(err)
        return Fail(message='Error When Creating Check object: ' + pformat(err))

    if result.fail:
        return result

    checkNode=result.data

    #Now we need to build the tree structure

    node=systemcheck.utils.get_or_create(session, model=systemcheck.checks.models.Check, parent_id=None)

    logger.debug('Building Tree Structure for %s', pformat(data.get('treepath')))

    for level, branch in enumerate(data.get('treepath')):
        name = branch.get('name')
        saClassname = branch.get('type')
        description = branch.get('description')
        logger.debug('Level: %s, Name: %s, Class: %s', str(level), name, saClassname)

        saClass = models.get_class_by_name(models.meta.Base, saClassname)

        nodeFound=False

        for child in node.children:
            if isinstance(child, saClass) and child.name==branch.get('name'):
                logger.debug('Found existing node "%s" ', name)
                node=child
                nodeFound = True
                break

        if not nodeFound:
            logger.debug('Node with name %s and class %s does not exist. Create new', name, saClassname)
            node = saClass(name=name, description=description, parent_node=node)

    models.meta.base.Base.metadata.create_all(session.bind)

    try:
        session.commit()
    except Exception as err:
        return Fail(message='Error During Import: '.format(pformat(err)))

    # Finally, adding the object to the tree

    node.children.append(checkNode)

    try:
        session.commit()
    except Exception as err:
        return Fail(message='Error During Import: '.format(pformat(err)))

    return Result(data=checkNode)

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