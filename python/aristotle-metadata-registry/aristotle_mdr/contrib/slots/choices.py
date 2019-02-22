from model_utils import Choices

permission_choices = Choices(
    (0, 'public', 'Public'),
    (1, 'auth', 'Authenticated'),
    (2, 'workgroup', 'Workgroup'),
)
