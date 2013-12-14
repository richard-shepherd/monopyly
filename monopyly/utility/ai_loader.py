import os
import imp


def load_ais():
    '''
    Finds packages containing AIs from the root->AIs folder and returns
    a list of the AI objects they contain.
    '''
    # We find the AI package folders, which all being with "AI_"...
    ai_folders = [item for item in os.listdir("AIs") if item.startswith("AI_")]

    # We load each package, and create an instance of their AI object...
    ais = []
    for ai_folder in ai_folders:
        package_folder = "AIs/" + ai_folder
        ai_package = imp.load_package(ai_folder, package_folder)
        ais.append(ai_package.AI())

    return ais