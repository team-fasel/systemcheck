

class MockConnection():
    """Mock PyRFC object
    This is a quick and dirty object to simulate the responses of a real RFC connection. This allows the testing of the
    connection object without requiring a SAP system
    """

    def __init__(self, logoninfo:dict=None, mockdata:dict=None):
        self.logoninfo=logoninfo
        self.mockdata = mockdata

    def call(self, *args, **kwargs):
        if args[0]=='TH_SERVER_LIST':
            return {'LIST': [{'HOST': 'sap001', 'NAME': 'sap001_S01_10', 'SERV': 'sapdp10'},
                                         {'HOST': 'sap002', 'NAME': 'sap002_S01_10', 'SERV': 'sapdp10'}],
                                'LIST_IPV6': [{'HOST': 'sap001', 'NAME': 'sap001_S01_10', 'SERV': 'sapdp10'},
                                              {'HOST': 'sap002', 'NAME': 'sap002_S01_10', 'SERV': 'sapdp10'}]}

        elif args[0]=='RFC_READ_TABLE':
            if kwargs.get('QUERY_TABLE')=='T000' and kwargs.get('NO_DATA')=='X':
                return {'DATA': [],
                        'FIELDS': [{'FIELDNAME': 'MANDT',
                                    'FIELDTEXT': 'Client',
                                    'LENGTH': '000003',
                                    'OFFSET': '000000',
                                    'TYPE': 'C'},
                                   {'FIELDNAME': 'MTEXT',
                                    'FIELDTEXT': 'Client name',
                                    'LENGTH': '000025',
                                    'OFFSET': '000003',
                                    'TYPE': 'C'}],
                         'OPTIONS': []}
            elif kwargs.get('QUERY_TABLE') == 'T000' and kwargs.get('ROWSKIPS')==0:
                return {'DATA': [{'WA': '000SAP AG'},
                                 {'WA': '100Standard Client'}],
                        'FIELDS': [{'FIELDNAME': 'MANDT',
                                    'FIELDTEXT': 'Client',
                                    'LENGTH': '000003',
                                    'OFFSET': '000000',
                                    'TYPE': 'C'},
                                   {'FIELDNAME': 'MTEXT',
                                    'FIELDTEXT': 'Client name',
                                    'LENGTH': '000025',
                                    'OFFSET': '000003',
                                    'TYPE': 'C'}],
                         'OPTIONS': []}
            elif kwargs.get('QUERY_TABLE') == 'T000' and kwargs.get('ROWSKIPS')>0:
                return {'DATA': [],
                        'FIELDS': [{'FIELDNAME': 'MANDT',
                                    'FIELDTEXT': 'Client',
                                    'LENGTH': '000003',
                                    'OFFSET': '000000',
                                    'TYPE': 'C'},
                                   {'FIELDNAME': 'MTEXT',
                                    'FIELDTEXT': 'Client name',
                                    'LENGTH': '000025',
                                    'OFFSET': '000003',
                                    'TYPE': 'C'}],
                         'OPTIONS': []}

    def get_connection_attributes(self):
        return {'active_unit': False, 'client': '000', 'codepage': '4103', 'cpicConvId': '98815493',  'dest': '',
                'host': 'win10', 'isoLanguage': 'EN', 'kernelRel': '745', 'language': 'E',
                'partnerBytesPerChar': '2',  'partnerCodepage': '4103', 'partnerHost': 'sap001',
                'partnerRel': '740', 'partnerSystemCodepage': '4103', 'partnerType': '3',  'progName': 'SAPLSYST',
                'rel': '742', 'reserved': '', 'rfcRole': 'C', 'sysId': 'E01', 'sysNumber': '00',  'trace': '0',
                'type': 'E', 'user': 'TEST'}

class MockResults():

    def __init__(self):
        pass


