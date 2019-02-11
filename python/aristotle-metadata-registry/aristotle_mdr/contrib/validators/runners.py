from typing import List, Iterable

import attr
import json
import jsonschema
import logging
import yaml

from django.conf import settings
from django.utils.module_loading import import_string
from os import path

from aristotle_mdr.contrib.validators import models
from aristotle_mdr.contrib.validators.schema.load import load_schema
from aristotle_mdr.models import _concept, STATES

logger = logging.getLogger(__name__)


@attr.s
class ValidationRunner:
    registration_authority = attr.ib()
    state = attr.ib()

    def get_schema(self):
        return load_schema()

    def get_validators(self):
        if hasattr(self, 'validators'):
            return self.validators
        else:
            aristotle_validators = settings.ARISTOTLE_VALIDATORS
            self.validators = {x: import_string(y) for x, y in aristotle_validators.items()}
            return self.validators

    def run_rule(self, rule, item, target_state, ra=None) -> List[str]:
        validators = self.get_validators()
        rule_state = rule['status']
        object_type = rule.get('object', None)
        # Instanciated validators for this rules checks
        rule_validators = [
            validators[check['validator']](check)
            for check in rule['checks']
            if check['validator'] in self.validators
        ]
        # Get item info
        item = item.item
        itemtype = type(item).__name__
        # Check if the rule needs to be run
        if object_type not in [None, itemtype, "any"]:
            return []
        if rule_state not in [STATES[target_state], "any"]:
            return []
        # Run validators
        results = []
        for validator in rule_validators:
            status, message = validator.validate(item, ra)

            results.append({
                'validator': validator,
                'rule': validator.rule,
                'status': status,
                'message': message
            })
        return results

    def get_rulesets(self) -> List:
        """Need to be overwritten to return a list conforming to schema"""
        raise NotImplementedError

    def validate_rules(self):
        try:
            jsonschema.validate(ruleset, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            logger.critical(e)

    def validate_metadata(self, metadata: Iterable[_concept]) -> List:
        rulesets = self.get_rulesets()
        schema = self.get_schema()

        total_results = []
        for concept in metadata:
            kwargs = {}

            # Slow query
            item = concept.item

            results = []
            for rule in rulesets:
                results += self.run_rule(rule, item, self.state, self.registration_authority)

            kwargs['results'] = results
            kwargs['item_name'] = item.name

            total_results.append(kwargs)

        return total_results


class FileValidationRunner(ValidationRunner):

    def get_rulesets(self):
        with open(settings.ARISTOTLE_VALIDATION_FILERUNNER_PATH) as setupfile:
            ruleset = yaml.safe_load(setupfile)

        return ruleset


class DatabaseValidationRunner(ValidationRunner):

    def get_rulesets(self):
        rules_yaml = []
        site_rules = models.RegistryValidationRules.objects.first()
        try:
            ra_rules = models.RAValidationRules.objects.get(
                registration_authority=self.registration_authority
            )
        except models.RAValidationRules.DoesNotExist:
            ra_rules = None

        if site_rules:
            rules_yaml.append(site_rules.rules)
        if ra_rules:
            rules_yaml.append(ra_rules.rules)

        rules = []
        for ryaml in rules_yaml:
            rules += yaml.safe_load(ryaml)

        return rules
