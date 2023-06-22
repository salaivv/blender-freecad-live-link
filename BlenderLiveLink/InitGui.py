import FreeCADGui as Gui


def runStartupMacros(name):
    if name != "NoneWorkbench":
        Gui.getMainWindow().workbenchActivated.disconnect(runStartupMacros)
        import BlenderLiveLink
        BlenderLiveLink.create_menu()


import __main__
__main__.runStartupMacros = runStartupMacros

Gui.getMainWindow().workbenchActivated.connect(runStartupMacros)