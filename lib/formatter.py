def set_color(string, level=None):
    """
    set the color for the output string
    """
    color_levels = {
        10: "\033[36m{}\033[0m",
        20: "\033[32m{}\033[0m",
        30: "\033[33m{}\033[0m",

        40: "\033[1m\033[91m{}\033[0m",
        50: "\033[31m{}\033[0m"
    }
    if level is None:
        level = 20
    return color_levels[level].format(string)


def info(string):
    """
    outputs an information string in green
    """
    print(
        "[{}] {}".format(set_color("info", level=20), string)
    )


def warn(string):
    """
    outputs a wanring string in yellow
    """
    print(
        "[{}] {}".format(set_color("warning", level=30), string)
    )


def error(string):
    """
    outputs an error string in red
    """
    print(
        "[{}] {}".format(set_color("error", level=40), string)
    )
