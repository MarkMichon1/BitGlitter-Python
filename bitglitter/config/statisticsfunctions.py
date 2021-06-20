from bitglitter.config.statistics import stats_manager


def output_stats():
    """Returns a dictionary object containing read and write statistics."""

    return stats_manager.return_stats()


def clear_stats():
    """Resets all write and read values back to zero."""

    stats_manager.clear_stats()
