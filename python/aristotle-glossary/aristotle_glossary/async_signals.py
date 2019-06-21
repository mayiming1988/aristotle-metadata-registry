from aristotle_mdr.contrib.async_signals.utils import safe_object
from aristotle_glossary.models import reindex_metadata_item

import logging
logger = logging.getLogger(__name__)


def reindex_metadata_item_async(message, **kwargs):
    instance = safe_object(message)
    reindex_metadata_item(instance)
