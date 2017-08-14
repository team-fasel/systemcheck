from systemcheck.utils import get_or_create
from systemcheck.checks.models import Check
from systemcheck.utils import get_or_create


from systemcheck.systems.ABAP.plugins.actions.check_abap_count_table_entries import CheckAbapCountTableEntries, CheckAbapCountTableEntries__params
from systemcheck.systems.ABAP.models import CheckABAPFolder
from systemcheck.systems.generic.models import GenericSystemTreeNode
from systemcheck.systems.ABAP.models import SystemABAPFolder, SystemABAPClient, SystemABAP


def populateChecksTree(session):


    rootnode = get_or_create(session, Check, parent_id=None, name='RootNode')
    auth_folder = CheckABAPFolder(name='Authorization', parent_node=rootnode)
    basis_folder = CheckABAPFolder(name='Basis', parent_node=rootnode)
    post_install_folder = CheckABAPFolder(name='Post Install', parent_node=basis_folder)
    check=CheckAbapCountTableEntries(name ='Clients 001 and 066 removed',
                                       description ='If client 001 is not actively used, it can be deleted. Client 066 is no longer required in any case',
                                     )

    param001 = CheckAbapCountTableEntries__params(
        param_set_name = 'Client 001',
        table_name ='T000',
        table_fields ='MANDT',
        expected_count = 0,
        operator='NE',
        where_clause="MANDT EQ '001'"
    )
    param066 = CheckAbapCountTableEntries__params(
        param_set_name = 'Client 066',
        table_name='T000',
        table_fields='MANDT',
        expected_count=0,
        operator='NE',
        where_clause="MANDT EQ '066'"
    )
    check.params.append(param001)
    check.params.append(param066)
    post_install_folder.children.append(check)
    session.commit()


def populateSystemsABAPTree(session):

    rootnode = get_or_create(session, GenericSystemTreeNode, parent_id=None, name='RootNode')
#    rootnode = session.query(GenericSystemTreeNode).filter_by(parent_id=None).one()

    dev_folder = SystemABAPFolder(name='DEV', parent_node=rootnode)
    qas_folder = SystemABAPFolder(name='QAS', parent_node=rootnode)
    prd_folder = SystemABAPFolder(name='PRD', parent_node=rootnode)
    sbx_folder = SystemABAPFolder(name='SBX', parent_node=rootnode)

    e1d_abap = SystemABAP(sid='E1D', tier='Dev', rail='N', name='E1D',
                          description='ECC Development System',
                          enabled=True,
                          snc_partnername="Fill SNC Name Here",
                          snc_qop='9',
                          use_snc=True,
                          default_client='100',
                          ms_hostname='sape1d.team-fasel.lab',
                          ms_sysnr='00',
                          ms_logongroup='PUBLIC')

    dev_folder.children.append(e1d_abap)

    e1d_client000 = SystemABAPClient(client='000')
    e1d_abap.children.append(e1d_client000)
    e1d_client100 = SystemABAPClient(client='100')
    e1d_abap.children.append(e1d_client100)

    e1s_abap = SystemABAP(sid='E1S', tier='Sandbox', rail='N', name='E1S',
                          description='ECC Sandbox System',
                          enabled=True,
                          snc_partnername="Fill SNC Name Here",
                          snc_qop='9',
                          use_snc=True,
                          default_client='100',
                          ms_hostname='sape1s.team-fasel.lab',
                          ms_sysnr='00',
                          ms_logongroup='PUBLIC')

    sbx_folder.children.append(e1s_abap)

    e1s_client000 = SystemABAPClient(client='000')
    e1s_abap.children.append(e1s_client000)
    e1s_client100 = SystemABAPClient(client='100')
    e1s_abap.children.append(e1s_client100)

    session.commit()