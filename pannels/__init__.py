import pkgutil, os

currentPath = os.path.dirname(os.path.abspath(__file__))

dirs = [d for d in list(os.walk("./pannels/"))[0][1] if "__" not in d]

folders = {}
foldersINV = {}
packages = {}
__all__ = []
for d in dirs:
    folders[d] = []
    for loader, module_name, is_pkg in pkgutil.walk_packages([f"{currentPath}/{d}"]):
        _module = loader.find_module(module_name).load_module(module_name)
        globals()[module_name] = _module
        packages[module_name] = (_module)
        __all__.append(module_name)
        folders[d].append(module_name)
        foldersINV[module_name] = d

print(f"Pannels that where loaded: {__all__}")