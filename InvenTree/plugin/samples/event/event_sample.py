"""
Sample plugin which responds to events
"""

import warnings

from django.conf import settings

from plugin import InvenTreePlugin
from plugin.mixins import EventMixin


class EventPluginSample(EventMixin, InvenTreePlugin):
    """
    A sample plugin which provides supports for triggered events
    """

    NAME = "EventPlugin"
    SLUG = "sampleevent"
    TITLE = "Triggered Events"

    def process_event(self, event, *args, **kwargs):
        """ Custom event processing """

        print(f"Processing triggered event: '{event}'")
        print("args:", str(args))
        print("kwargs:", str(kwargs))

        # Issue warning that we can test for
        if settings.PLUGIN_TESTING:
            warnings.warn(f'Event `{event}` triggered')
