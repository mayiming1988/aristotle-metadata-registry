from aristotle_mdr.contrib.issues.models import IssueLabel
from aristotle_mdr.forms.utils import StewardOrganisationRestrictedChoicesForm


class IssueLabelEditForm(StewardOrganisationRestrictedChoicesForm):
    class Meta:
        model = IssueLabel
        fields = '__all__'
