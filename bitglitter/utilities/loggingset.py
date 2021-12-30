import datetime
import logging
import os

from bitglitter.validation.utilities import logging_config_validate


def logging_setter(logging_level, logging_stdout_output, logging_txt_output, logging_save_path=None):
    """This is what the logging level and output during the write operation.  It's worth nothing that this is the ONLY
    function that checks parameters outside of verify_write_parameters, because that function's logging outputs hinge in
    the configuration for logging.
    """

    logging_config_validate(logging_level, logging_stdout_output, logging_txt_output)
    logging_level_dict = {None: None, False: None, 'debug': logging.DEBUG, 'info': logging.INFO}
    if logging_txt_output:
        if not os.path.isdir(logging_save_path):
            os.makedirs(logging_save_path)
        log_output_name = f"logs\\{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
        output_log = logging.getLogger()
        output_log_handler = logging.FileHandler(log_output_name)
        output_log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        output_log_handler.setFormatter(output_log_formatter)
        if not output_log.handlers:
            output_log.addHandler(output_log_handler)
        output_log.setLevel(logging_level_dict[logging_level])

    if logging_stdout_output:
        print_log = logging.getLogger()
        print_log_handler = logging.StreamHandler()
        print_log_formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s %(message)s", "%H:%M:%S")
        print_log_handler.setFormatter(print_log_formatter)
        if not print_log.handlers:
            print_log.addHandler(print_log_handler)
        print_log.setLevel(logging_level_dict[logging_level])
