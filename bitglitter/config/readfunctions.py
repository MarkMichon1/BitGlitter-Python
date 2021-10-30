from bitglitter.config.config import session
from bitglitter.config.readmodels.readmodels import StreamSha256Blacklist
from bitglitter.config.readmodels.streamread import StreamRead


def unpackage(stream_sha256):
    pass #unpackage as much of the file as possible


def return_all_read_information():
    pass


def return_single_read(stream_sha256):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256)
    if not stream_read:
        return {}
    else:
        return {}


def attempt_password(stream_sha256, encryption_key, attempt_unpackaging, scrypt_n=None, scrypt_r=None, scrypt_p=None):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256)
    if not stream_read:
        return False

    # Fetch streamsha

    # If stream is decrypted already or crypto not enabled, return True

    """3"""

    if '':
        return False

    if attempt_unpackaging:
        pass
    return True
    #     if password_update:
    #         proper_string_syntax('password_update', password_update)
    #     if scrypt_n:
    #         is_int_over_zero('scrypt_n', scrypt_n)

def return_stream_manifest(stream_sha256):
    pass


def remove_partial_save(stream_sha256):
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256)
    if not stream_read:
        return False
    stream_read.delete()
    return True


def remove_all_partial_save_data():
    """Removes all data for partial saves, both files and metadata within some internal classes."""
    session.query(StreamRead).delete()
    return True


def update_stream_read(stream_sha256, auto_delete_finished_stream=None, unpackage_files=None): #todo test...
    if not isinstance(auto_delete_finished_stream, bool):
        raise ValueError('auto_delete_finished_stream must be type bool')
    stream_read = StreamRead.query(StreamRead.stream_sha256 == stream_sha256)
    if not stream_read:
        return False
    if auto_delete_finished_stream:
        stream_read.auto_delete_finished_stream = auto_delete_finished_stream
    if unpackage_files:
        stream_read.unpackage_files = unpackage_files
    stream_read.save()
    return True


def blacklist_stream_sha256(stream_sha256):
    stream_read = session.query(StreamRead).filter(StreamRead.stream_sha256 == stream_sha256).all()
    if stream_read:
        stream_read.delete()
    StreamSha256Blacklist.create(stream_sha256=stream_sha256)
    return True


def return_all_blacklist_sha256():
    returned_list = []
    blacklisted_streams = session.query(StreamSha256Blacklist).all()
    for blacklisted_item in blacklisted_streams:
        returned_list.append(blacklisted_item.stream_sha256)
    return returned_list


def remove_blacklist_sha256(stream_sha256):
    blacklist =  session.query(StreamSha256Blacklist).filter(StreamSha256Blacklist.stream_sha256 == stream_sha256)\
        .first()
    if not blacklist:
        return False
    blacklist.delete()
    return True


def remove_all_blacklist_sha256():
    session.query(StreamSha256Blacklist).delete()
    session.commit()
    return True
