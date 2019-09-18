from aristotle_mdr.contrib.aristotle_backwards import models
from aristotle_mdr.register import register_concept


register_concept(
    models.ClassificationScheme,
    reversion={
        'follow': ['valueDomains']
    }
)
