import pkgutil
import importlib

def discover_workflows():
    """
    Automatically discovers and imports all workflow modules within this package.
    This triggers their registration with the central WorkflowRegistry.
    """
    from . import registry  # Ensure registry is initialized
    
    # Iterate through all subdirectories (sub-packages) in the current package
    for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
        if is_pkg and module_name.startswith("wf"):
            # Import the sub-package (e.g. 'workflow.wf001_inventory_restock')
            importlib.import_module(f".{module_name}", package=__name__)
