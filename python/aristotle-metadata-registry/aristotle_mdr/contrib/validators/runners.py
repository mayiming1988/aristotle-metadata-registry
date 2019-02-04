from typing import List

import attr
import json
import jsonschema
import logging
import yaml

from django.conf import settings
from django.utils.module_loading import import_string
from os import path

from aristotle_mdr.contrib.validators.validators import RuleChecker
from aristotle_mdr.contrib.validators.schema.load import load_schema

logger = logging.getLogger(__name__)


@attr.s
class ValidationRunner:
    registration_authority = attr.ib()
    state = attr.ib()

    def __attrs_post_init__(self):
        aristotle_validators = settings.ARISTOTLE_VALIDATORS
        self.validators = {x: import_string(y) for x, y in aristotle_validators.items()}
        self.schema = self.load_schema()
        self.rulesets = self.load_rulesets()

    def load_schema(self):
        return load_schema()

    def load_rulesets(self) -> List[RuleChecker]:
        raise NotImplementedError

    def validate_rules(self):
        try:
            jsonschema.validate(ruleset, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            logger.critical(e)

    def validate_metadata(self, metadata) -> List:
        total_results = []
        for concept in metadata:
            kwargs = {}

            # Slow query
            item = concept.item

            results = []
            for checker in self.rulesets:
                results += checker.run_rule(item, self.state, self.registration_authority)

            kwargs['results'] = results
            kwargs['item_name'] = item.name

            total_results.append(kwargs)

        return total_results


class FileValidationRunner(ValidationRunner):
    def load_rulesets(self):
        with open(settings.ARISTOTLE_VALIDATION_FILERUNNER_PATH) as setupfile:
            ruleset = yaml.safe_load(setupfile)

        return [RuleChecker(rule) for rule in ruleset]
