from bitglitter.config.config import session
from bitglitter.config.readmodels.readmodels import StreamSHA256Blacklist
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.read.decode.headerdecode import metadata_header_validate_decode
from bitglitter.utilities.loggingset import logging_setter

logging_setter('info', True, False)


def unpackage(stream_sha256):
    """Attempt to unpackage as much of the file as possible.  Returns None if stream doesn't exist, returns False if
    there is a decryption error.
    """

    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return None
    results = stream_read.attempt_unpackage()
    stream_read.autodelete_attempt()
    return results #todo + readme


def return_all_read_information(advanced=False):
    stream_reads = []
    returned_list = []
    for stream_read in stream_reads:
        returned_list.append(stream_read.return_state(advanced))
    return returned_list


def return_single_read(stream_sha256, advanced=False):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    else:
        return stream_read.return_state(advanced)


def update_decrypt_values(stream_sha256, decryption_key=None, scrypt_n=None, scrypt_r=None, scrypt_p=None):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    if not stream_read.encryption_enabled:
        return True

    if decryption_key:
        stream_read.decryption_key = decryption_key
    if scrypt_n:
        stream_read.scrypt_n = scrypt_n
    if scrypt_r:
        stream_read.scrypt_r = scrypt_r
    if scrypt_p:
        stream_read.scrypt_p = scrypt_p
    stream_read.save()

    return True


def return_stream_manifest(stream_sha256):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return {'error': 'No stream read'}
    if not stream_read.manifest_string:
        if not stream_read.metadata_header_bytes:
            return {'error': 'Metadata header not decoded yet'}


def remove_partial_save(stream_sha256):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256)
    if not stream_read:
        return False
    stream_read.delete()
    return True


def remove_all_partial_save_data():
    """Removes all data for partial saves, both files and metadata within some internal classes."""
    session.query(StreamRead).delete()
    session.commit()
    return True


def update_stream_read(stream_sha256, auto_delete_finished_stream=None,
                       auto_unpackage_stream=None):  # todo test... & README
    if not isinstance(auto_delete_finished_stream, bool):
        raise ValueError('auto_delete_finished_stream must be type bool')
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256)
    if not stream_read:
        return False
    if auto_delete_finished_stream:
        stream_read.auto_delete_finished_stream = auto_delete_finished_stream
    if auto_unpackage_stream:
        stream_read.auto_unpackage_stream = auto_unpackage_stream
    stream_read.save()
    return True


def blacklist_stream_sha256(stream_sha256):
    stream_read = session.query(StreamRead).filter(StreamRead.stream_sha256 == stream_sha256).all()
    if stream_read:
        stream_read.delete()
    StreamSHA256Blacklist.create(stream_sha256=stream_sha256)
    return True


def return_all_blacklist_sha256():
    returned_list = []
    blacklisted_streams = session.query(StreamSHA256Blacklist).all()
    for blacklisted_item in blacklisted_streams:
        returned_list.append(blacklisted_item.stream_sha256)
    return returned_list


def remove_blacklist_sha256(stream_sha256):
    blacklist = session.query(StreamSHA256Blacklist).filter(StreamSHA256Blacklist.stream_sha256 == stream_sha256) \
        .first()
    if not blacklist:
        return False
    blacklist.delete()
    return True


def remove_all_blacklist_sha256():
    session.query(StreamSHA256Blacklist).delete()
    session.commit()
    return True
