import datetime
import logging
import os


def logging_setter(logging_level, logging_print, logging_save_output):
    '''This is what the logging level and output during the write operation.  It's worth nothing that this is the ONLY
    function that checks parameters outside of verify_write_parameters, because that function's logging outputs hinge in
    the configuration for logging.
    '''

    # First, we're checking the parameters are valid.
    acceptable_level_words = [False, 'debug', 'info']
    if logging_level not in acceptable_level_words:
        raise ValueError(f"{logging_level} is not a valid input for loggingLevel.  Only 'info', 'debug', and False are "
                         f"allowed.")

    if not isinstance(logging_print, bool):
        raise ValueError("Only booleans are allowed for loggingPrint.")

    if not isinstance(logging_save_output, bool):
        raise ValueError("Only booleans are allowed for loggingSaveOutput.")

    logging_level_dict = {False: None, 'debug': logging.DEBUG, 'info': logging.INFO}

    # Next, we're setting each of the loggers if they are enabled.
    if logging_save_output:

        if not os.path.isdir('logs'):
            os.mkdir('logs')
        log_output_name= f"logs\\{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
        output_log = logging.getLogger()
        output_log_handler = logging.FileHandler(log_output_name)
        output_log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        output_log_handler.setFormatter(output_log_formatter)
        output_log.addHandler(output_log_handler)
        output_log.setLevel(logging_level_dict[logging_level])

    if logging_print:

        print_log = logging.getLogger()
        print_log_handler = logging.StreamHandler()
        print_log_formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s %(message)s", "%H:%M:%S")
        print_log_handler.setFormatter(print_log_formatter)
        print_log.addHandler(print_log_handler)
        print_log.setLevel(logging_level_dict[logging_level])