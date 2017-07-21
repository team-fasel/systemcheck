from systemcheck.systems.ABAP.models import AbapClient
from pprint import pprint

client = AbapClient(client='000', username='User01', password='Password01')

pprint(client.username)
