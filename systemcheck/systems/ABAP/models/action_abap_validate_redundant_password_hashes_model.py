from systemcheck.systems.ABAP.models import AbapSpoolParams_BAPIPRIPAR_Mixin, ActionAbapIsNotClientSpecificMixin
from systemcheck import models
from systemcheck.models.meta import generic_repr
from systemcheck.checks.models import Check

pluginName='ActionAbapValidateRedundantPasswordHashes'

@generic_repr
class ActionAbapValidateRedundantPasswordHashes(Check, AbapSpoolParams_BAPIPRIPAR_Mixin, ActionAbapIsNotClientSpecificMixin):

    __tablename__ = pluginName

    id = models.meta.Column(models.meta.Integer, models.meta.ForeignKey('checks_metadata.id'), primary_key=True)
    SAP_USER_NAME = models.meta.Column(models.meta.String(12),
                       qt_label='Step User',
                       qt_description='Background User Name for Authorization Check',
                       nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':pluginName,
    }

    __qtmap__ = [Check.name, Check.description, Check.failcriteria, Check.criticality,
                 SAP_USER_NAME,
                 AbapSpoolParams_BAPIPRIPAR_Mixin.PDEST,
                 AbapSpoolParams_BAPIPRIPAR_Mixin.PRBIG,
                 AbapSpoolParams_BAPIPRIPAR_Mixin.PRSAP]