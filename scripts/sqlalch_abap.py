from systemcheck import SESSION
from systemcheck.systems.ABAP.models import AbapTreeNode, AbapSystem, AbapClient
import sqlalchemy_utils
from pprint import pprint

def populate_tree():
    rootnode = SESSION.query(AbapTreeNode).filter_by(type='ROOT').first()


    dev_folder=AbapTreeNode(type='FOLDER', name='DEV', parent_node=rootnode)
    qas_folder=AbapTreeNode(type='FOLDER', name='QAS', parent_node=rootnode)
    prd_folder=AbapTreeNode(type='FOLDER', name='PRD', parent_node=rootnode)
    sbx_folder=AbapTreeNode(type='FOLDER', name='SBX', parent_node=rootnode)

    e1d_node = AbapTreeNode(type='ABAP', parent_node=dev_folder, name='E1D')
    e1d_abap = AbapSystem(sid='E1D', tier = 'Dev', rail = 'N',
                          description= 'ECC Development System',
                          enabled = True,
                          snc_partnername = "Fill SNC Name Here",
                          snc_qop='9',
                          use_snc=True,
                          default_client='100',
                          ms_hostname='sape1d.team-fasel.lab',
                          ms_sysnr='00',
                          ms_logongroup='PUBLIC')

    e1d_node.abap_system=e1d_abap

    e1d_client000 = AbapClient(client='000')
    e1d_client000_node=AbapTreeNode(type=e1d_client000.RELNAME, name='000', parent_node=e1d_node)
    e1d_client000_node.abap_client=e1d_client000
    e1d_client100 = AbapClient(client='100')
    e1d_client100_node=AbapTreeNode(type=e1d_client100.RELNAME, name='100', parent_node=e1d_node)
    e1d_client100_node.abap_client=e1d_client100


    e1s_abap = AbapSystem(sid='E1S', tier = 'Sandbox', rail = 'N',
                          description= 'ECC Sandbox System',
                          enabled = True,
                          snc_partnername = "Fill SNC Name Here",
                          snc_qop='9',
                          use_snc=True,
                          default_client='100',
                          ms_hostname='sape1s.team-fasel.lab',
                          ms_sysnr='00',
                          ms_logongroup='PUBLIC')
    e1s_node = AbapTreeNode(type=e1s_abap.RELNAME, parent_node=sbx_folder, name='E1S')
    e1s_node.abap_system=e1s_abap

    e1s_client000 = AbapClient(client='000')
    e1s_client000_node=AbapTreeNode(type=e1s_client000.RELNAME, name='000', parent_node=e1s_node)
    e1s_client000_node.abap_client=e1s_client000
    e1s_client100 = AbapClient(client='100')
    e1s_client100_node=AbapTreeNode(type=e1s_client100.RELNAME, name='100', parent_node=e1s_node)
    e1s_client100_node.abap_client=e1s_client100


    pprint(rootnode._dump())
    SESSION.commit()

if __name__ == '__main__':
    from pprint import pprint
    #populate_tree()
#    node=SESSION.query(AbapTreeNode).filter_by(type='ROOT')[0]
    populate_tree()

#    print(node._info_by_colnr(1))