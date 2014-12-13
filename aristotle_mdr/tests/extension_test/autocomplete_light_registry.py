import autocomplete_light
import models
import aristotle_mdr.autocomplete_light_registry as reg

autocompletesToRegister = [
        models.Question,
    ]
for cls in autocompletesToRegister:
    # This will generate a PersonAutocomplete class
    x = reg.autocompleteTemplate.copy()
    x['name']='Autocomplete'+cls.__name__
    autocomplete_light.register(cls,reg.PermissionsAutocomplete,**x)
