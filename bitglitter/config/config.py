import pickle

from bitglitter.config.configobjects import Config

# Attempts to load previous session, otherwise it creates a few Config object.
try:
    with open ('config.pickle', 'rb') as pickleLoad:
        config = pickle.load(pickleLoad)

except:
    config = Config()