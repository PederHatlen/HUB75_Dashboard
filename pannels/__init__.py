import pkgutil, os, sys, importlib.util

excluded = [] #["Spotify"]

currentPath = os.path.dirname(os.path.abspath(__file__))

dirs = [d for d in list(os.walk("./pannels/"))[0][1] if "__" not in d]

folders = {}
foldersINV = {}
packages = {}
__all__ = []
for d in dirs:
    folders[d] = []
    for finder, module_name, is_pkg in pkgutil.walk_packages([f"{currentPath}/{d}"]):
        try:
            if module_name in excluded: continue
            spec = finder.find_spec(module_name)
            if spec is None: continue

            _module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = _module
            spec.loader.exec_module(_module)
            globals()[module_name] = _module
            packages[module_name] = (_module)
            __all__.append(module_name)
            folders[d].append(module_name)
            foldersINV[module_name] = d
        except Exception as E: print(f"Startup: Could not load {module_name}: {E}")

print(f"Startup: Loaded pannels: {__all__}")
