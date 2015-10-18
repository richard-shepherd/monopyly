import os
import imp
import inspect


def _find_derived_classes(package, base_class):
    '''
    Finds classes exposed by the package which derive from base_class.

    An *instance* of each object of the types found is returned in
    a list.
    '''
    results = []

    # We look through the members of the package...
    members = inspect.getmembers(package)
    for member in members:
        try:
            # We check if the member is a class...
            member_type = member[1]
            if not inspect.isclass(member_type):
                continue

            # It is a class, so we create an instance to check
            # if it is derived from base_class...
            instance = member_type()
            if isinstance(instance, base_class):
                results.append(instance)
        except:
            continue

    return results

# Modified to allow different AI directory
def load_ais(base_folder="AIs"):
    '''
    Finds packages containing AIs from the root->AIs folder and returns
    a list of the AI objects they contain.
    '''
    from ..game import PlayerAIBase

    # We find the AI package folders, which live in the "AIs" folder...
    ai_folders = [item for item in os.listdir(base_folder)]

    # We loop through the packages...
    ais = []
    for ai_folder in ai_folders:
        if not ai_folder.startswith("."):
            # We load each package...
            package_folder = os.path.join(base_folder,ai_folder)
            print(package_folder)
            ai_package = imp.load_package(ai_folder, package_folder)

            # We find the classes they expose that are derived from the
            # base AI class...
            ais_in_package = _find_derived_classes(ai_package, PlayerAIBase)
            ais.extend(ais_in_package)

    return ais