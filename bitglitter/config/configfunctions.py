import os

from bitglitter.config.config import config #todo

# These functions are for end users.




def remove_session():
    '''Tries to remove the session pickle if it exists, clearing all statistics and custom colors.'''

    try:
        config.assembler.clear_partial_saves()
        os.remove('config.pickle')
    except:
        pass
