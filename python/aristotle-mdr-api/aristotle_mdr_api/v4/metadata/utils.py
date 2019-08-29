# from django.template.defaultfilters import slugify
# from django.urls import reverse
#
#
# def url_slugify_metadata_api(item):
#     item_model = item.item_type.model_class()
#     slug = slugify(item.name)[:50]
#     if not slug:
#         slug = "--"
#     return reverse(
#         "aristotle:item",
#         kwargs={'iid': item.pk, 'model_slug': item_model._meta.model_name, 'name_slug': slug}
#     )
