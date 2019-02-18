from aristotle_mdr import messages
from aristotle_mdr.contrib.async_signals.utils import safe_object


def review_request_created(message, **kwargs):
    review_request = safe_object(message)
    registration_authorities = [review_request.registration_authority]  # Maybe this becomes a many to many later
    concepts = []

    for concept in review_request.concepts.all():
        concepts.append(concept.name)
    for ra in registration_authorities:
        for registrar in ra.registrars.all():
            if registrar != review_request.requester:
                messages.review_request_created(recipient=registrar, obj=review_request, concepts=concepts)


def review_request_updated(message, **kwargs):
    review_request = safe_object(message)
    registration_authorities = [review_request.registration_authority]  # Maybe this becomes a many to many later
    concepts = []

    for concept in review_request.concepts.all():
        concepts.append(concept.name)

    for ra in registration_authorities:
        for registrar in ra.registrars.all():
            # TODO: WE NEED TO FIND A WAY TO CHECK IF THE SUBMITTER OF THE UPDATE IS THE CURRENT REGISTRAR IN THE LOOP:
            # if registrar != review_request.requester:
                messages.review_request_updated(recipient=registrar, obj=review_request, concepts=concepts)
