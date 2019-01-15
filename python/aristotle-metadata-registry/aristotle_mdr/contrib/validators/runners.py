from typing import List

import attr
import json
import jsonschema
import logging
import yaml

from django.conf import settings
from django.utils.module_loading import import_string
from os import path

from .validators import RuleChecker

logger = logging.getLogger(__name__)


@attr.s
class BaseValidationRunner:
    registration_authority = attr.ib()
    state = attr.ib()

    def __attrs_post_init__(self):
        aristotle_validators = settings.ARISTOTLE_VALIDATORS
        self.validators = {x: import_string(y) for x, y in aristotle_validators.items()}
        self.rulesets = self.load_rulesets()

    def load_rulesets(self) -> List:
        return []

    def validate_metadata(self, metadata):
        total_results = []
        for concept in metadata:
            kwargs = {}

            # TODO: Copied agin

            # Slow query
            item = concept.item

            results = []
            for rulesets in self.rulesets:
                for checker in rulesets:
                    # checker = RuleChecker(itemsetup)
                    results += checker.run_rule(item, self.state, self.registration_authority)

            kwargs['results'] = results
            kwargs['item_name'] = item.name

            total_results.append(kwargs)
        return total_results


class FileValidationRunner(BaseValidationRunner):
    def load_rulesets(self):
        # Hard coded setup for now
        with open(path.join(path.dirname(__file__), 'schema/schema.json')) as schemafile:
            self.schema = json.load(schemafile)

        with open(settings.ARISTOTLE_VALIDATION_FILERUNNER_PATH) as setupfile:
            ruleset = yaml.load(setupfile)

        try:
            jsonschema.validate(ruleset, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            logger.critical(e)
            return []

        return [[RuleChecker(rule) for rule in ruleset]]
