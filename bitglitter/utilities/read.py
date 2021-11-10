from bitglitter.config.config import session
from bitglitter.config.readmodels.readmodels import StreamFrame


def flush_active_frames():
    session.query(StreamFrame).filter(not StreamFrame.is_complete).delete()
    session.commit()
