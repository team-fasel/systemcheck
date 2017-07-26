import systemcheck.systems.ABAP.plugins as abapplugins


class EntryCount(abapplugins.CheckAbapRsusr002Plugin):

    def __init__(self):
        super().__init__()
