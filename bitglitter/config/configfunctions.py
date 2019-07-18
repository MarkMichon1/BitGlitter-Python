import os

from bitglitter.config.config import config

# These functions are for end users.

def output_stats(path):
    '''Writes a text file to a file path outlining usage statistics.'''

    active_path = os.path.join(os.getcwd(), path)
    with open(active_path + '\\BitGlitter statistics.txt', 'w') as writer:
        writer.write(str(config.stats_handler))


def clear_stats():
    '''Resets statistics back to zero in all fields.'''

    config.stats_handler.clear_stats()
    config.save_session()


def clear_session():
    '''Tries to remove the session pickle if it exists, clearing all statistics and custom colors.'''

    try:
        config.assembler.clear_partial_saves()
        os.remove('config.pickle')
    except:
        pass
