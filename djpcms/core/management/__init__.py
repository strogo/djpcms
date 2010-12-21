from optparse import OptionParser


def find_commands(management_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    """
    command_dir = os.path.join(management_dir, 'commands')
    try:
        return [f[:-3] for f in os.listdir(command_dir)
                if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []
    
    
class CommandFactory(object):
    
    def makeoptions(self):
        parser = OptionParser()
        commands = find_commands()
        for command in commands:
            parser.



def execute_manager():
    #utility = ManagementUtility(argv)
    utility.execute()