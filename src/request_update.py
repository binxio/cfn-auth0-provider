import json

"""
list of non-updatable properties.
"""
non_updatable_properties = {
    'Custom::Auth0Client': ['jwt.secret_encoded'],
    'Custom::Auth0ResourceServer': ['identifier']
}


def get_property_value_by_path(obj, path):
    """
    gets the value for the property from the dictionary. A dot is used to navigate the object.
    """
    for part in path.split('.'):
        value = obj[part] if obj is not None and isinstance(obj, dict) and part in obj else None
        obj = value
    return value


def remove_property_by_path(obj, path):
    """
    removes the property from the dictionary. A dot is used to navigate the object.
    """
    value = obj
    for part in path.split('.'):
        obj = value
        value = obj[part] if obj is not None and isinstance(obj, dict) and part in obj else None
    if value is not None:
        del obj[part]


def create_update_request(resource_type, old_request, update_request):
    """
    Creates an new update request, which excludes any of the non-updatable fields
    as specified in `non_updatable_properties` for the different resource_types.

    If the old value is missing or the value has not changed, the property will be removed
    from the update request.
    If the old value is different from the new value, the property will be left in the
    update request so that Auth0 can give the error.
    """
    update_request = json.loads(json.dumps(update_request))
    if resource_type in non_updatable_properties:
        for path in non_updatable_properties[resource_type]:
            old_value = value = get_property_value_by_path(update_request, path)
            print value
            if value is not None:
                old_value = get_property_value_by_path(old_request, path)
                print old_value
                if old_value == value or old_value is None:
                    remove_property_by_path(update_request, path)
    return update_request
