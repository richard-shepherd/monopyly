def is_iterable(object):
    '''
    Returns True if the object is iterable, False if it is not.
    '''
    try:
        i = iter(object)
    except TypeError:
        return False
    else:
        return True


def typecheck(object, type_or_prototype):
    '''
    Returns True if the object is of the type passed in.

    The type can be a straightforward type, such as int, list, or
    a class type. If so, we check that the object is an instance of
    the type.

    Alternatively the 'type' can be a prototype instance of a more
    complex type. For example:
    [int]                   a list of ints
    [(str, int)]            a list of (str, int) tuples
    {str: [(float, float)]} a dictionary of strings to lists of (float, float) tuples

    In these cases we recursively check the sub-items to see if they match
    the prototype.
    '''
    # If the type_or_prototype is a type, we can check directly against it...
    type_of_type = type(type_or_prototype)
    if type_of_type == type:
        return isinstance(object, type_or_prototype)

    # We have a prototype.

    # We check that the object is of the right type...
    if not isinstance(object, type_of_type):
        return False

    # We check each sub-item in object to see if it is of the right sub-type...
    if(isinstance(object, dict)):
        # The object is a dictionary, so we check that its items match
        # the prototype...
        prototype = type_or_prototype.popitem()
        for sub_item in object.items():
            if not validate_type(sub_item, prototype):
                return False

    elif(isinstance(object, tuple)):
        # For tuples, we check that each element of the tuple is
        # of the same type as each element the prototype...
        if len(object) != len(type_or_prototype):
            return False
        for i in range(len(object)):
            if not validate_type(object[i], type_or_prototype[i]):
                return False

    elif is_iterable(object):
        # The object is a non-dictionary collection such as a list or set.
        # For these, we check that all items in the object match the
        prototype = iter(type_or_prototype).__next__()
        for sub_item in object:
            if not validate_type(sub_item, prototype):
                return False

    else:
        # We don't know how to check this object...
        raise Exception("Can not validate this object")

    return True


