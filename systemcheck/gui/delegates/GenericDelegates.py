from PyQt5 import QtWidgets, QtCore, QtGui


class GenericStyledItemDelegateColumToRow(QtWidgets.QStyledItemDelegate):
    """ A Generic Delegate Class  for a table view that shows the columns as rows """

    def __init__(self):
        super().__init__()
        self.delegates={}
        self.delegates_alchemyObjects={}
        self.__itemView = None

    @property
    def itemView(self):
        return self.__itemView

    @itemView.setter
    def itemView(self, view):
        self.__itemView = view

    def insertRowDelegate(self, row, delegate, *args, alchemyObject=None, **kwargs):
        """ Insert a new Delegate

        :param row: The row of the delegate
        :param delegate: The class of the delegate
        :param alchemyObject: The SQLAlchemy column object

        """
        delegate.setParent(self, self)
        self.delegates[row]=delegate
        self.delegates_alchemyObjects[row]=alchemyObject

    def removeRowDelegate(self, row):
        if row in self.delegates.keys():
            del self.delegates[row]

    def paint(self, painter, option, index, *args, **kwargs):
        column=index.column()
        row=index.row()
        if column==1:
            delegate = self.delegates.get(row)
            if delegate is not None:
                delegate.paint(self, painter, option, index)
#            else:
#                QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
        else:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index, *args, **kwargs):
        column=index.column()
        row=index.row()
        if column==1:
            delegate = self.delegates.get(row)
            if delegate is not None:
                alchemyObject=self.delegates_alchemyObjects.get(row)
                return delegate.createEditor(self, parent, option, index, *args, alchemyObject=alchemyObject, **kwargs)
            else:
                return QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        column=index.column()
        row=index.row()
        if column==1:
            delegate = self.delegates.get(row)
            if delegate is not None:
                delegate.setEditorData(self, editor, index)
            else:
                QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)
        else:
            QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        column=index.column()
        row=index.row()
        if column==1:
            delegate=self.delegates.get(row)
            if delegate is not None:
                delegate.setModelData(self, editor, model, index)
        QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        column=index.column()
        row=index.row()
        if column==1:
            delegate = self.delegates.get(row)
            if delegate is not None:
                delegate.updateEditorGeometry(self, editor, option, index)
#            else:
#                QtWidgets.QStyledItemDelegate.paint(self, editor, option, index)
#        else:
#            QtWidgets.QStyledItemDelegate.paint(self, editor, option, index)

    def editorEvent(self, event, model, option, index):
        column=index.column()
        row=index.row()
        delegate = self.delegates.get(row)
        if delegate is not None:
            alchemyObject=self.delegates_alchemyObjects.get(row)
            result=delegate.editorEvent(self, event, model, option, index)
        else:
            result=QtWidgets.QStyledItemDelegate.editorvEent(self, event, model, option, index)
        return result