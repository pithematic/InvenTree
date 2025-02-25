"""sample implementation for IntegrationPlugin"""
from plugin import InvenTreePlugin
from plugin.mixins import UrlsMixin


class NoIntegrationPlugin(InvenTreePlugin):
    """
    An basic plugin
    """

    NAME = "NoIntegrationPlugin"


class WrongIntegrationPlugin(UrlsMixin, InvenTreePlugin):
    """
    An basic wron plugin with urls
    """

    NAME = "WrongIntegrationPlugin"
