from systems.ABAP.plugins.plugin_types import CheckAbapPlugin
from systemcheck.utils import Result, Fail

class AbapPlugin(CheckAbapPlugin):

    def __init__(self):
        super().__init__()

    def execute(self, conn, **kwargs):

        self.pluginResult.rating='pass'
        self.pluginResult.addResultColumn('RATING', 'Rating')
        self.pluginResult.addResultColumn('EXPECTED', 'Expected')
        self.pluginResult.addResultColumn('CONFIGURED', 'CONFIGURED')

        record=dict(EXPECTED='RFC_PING Successful')

        fm_result = conn.call_fm('RFC_PING')

        if fm_result.fail:
            record['CONFIGURED'] = fm_result.message
        else:
            record['CONFIGURED'] = 'RFC_PING Successful'

        if record['EXPECTED']==record['CONFIGURED']:
            record['RATING']='pass'
        else:
            record['RATING']='fail'
            self.pluginResult.rating='fail'

        self.pluginResult.add_result(record)

        return Result(data=self.pluginResult)


