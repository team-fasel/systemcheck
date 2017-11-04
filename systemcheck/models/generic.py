from systemcheck import models
from systemcheck.models.meta import Column, Integer, String, RichString, Boolean, validates



@models.meta.generic_repr
class NumberRange:
    """ A Number Range Implementation


    Unique numbers are important. This approach follows a similar approach as SAP's ABAP System. """

    __tablename__ = 'NumberRanges'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, qt_label='Number Range Name', nullable=False)
    value = Column(Integer, qt_label='Value', nullable=False, default=0)
    start = Column(Integer, qt_label='Value', nullable=True, default=0)
    end = Column(Integer, qt_label='Value', nullable=True, default=0)


    @validates('name')
    def convert_upper(self, key, value):
        return value.upper()

