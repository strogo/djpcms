'''
Install Packages.
This is usually needed during development
'''
import os
import sys

def install(debug):
    path = os.getcwd()
    home = os.path.split(path)[0]
    if home not in sys.path:
        sys.path.append(home)
        
    # Try to import. If failed throw the error
    import sitedjpcms
    
    # machines module is not provided for obvious security reasons.
    # machines_example is provided for illustration
    try:
        import machines
    except ImportError:
        import machine_example as machines
    
    # Get server setting
    sett    = machines.get_machine(sitedjpcms.__path__[0])
    # Set identity
    sett.id = machines.Identity()
    
    return sett
    
    