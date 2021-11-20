from bitglitter.config.config import session
from bitglitter.config.readmodels.readmodels import StreamFrame


def flush_inactive_frames():
    session.query(StreamFrame).filter(StreamFrame.is_complete == False).delete()
    session.commit()
