# -*- coding: utf-8 -*-
import sys
import sqlite3
import logging
from pinyin_dict import pinyin_dict


log = logging.getLogger("LD." + __name__)


def catch_except(errors=(Exception, ), default_value=False):
# Will wrap method with try/except and print parameters for easier debugging
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except sqlite3.Error as error:
                raise
            except errors as error:
                if not (hasattr(error, 'quiet') and error.quiet):
                    import traceback
                    traceback.print_exc()
                log.exception(error)
                log.error("function: %s \n args: %s \n kwargs: %s",
                          func.__name__, args, kwargs)
                return default_value

        return wrapper
    return decorator


def get_pinyin_first(u_char):
    char = ord(u_char)
    if char in pinyin_dict:
        return pinyin_dict[char][0]
    else:
        return ''


def get_sorttitle(title):
    return_list = []
    for one in title:
        return_list.append(get_pinyin_first(one))
        return_list.append(one)
    return ''.join(return_list)


def clear_progress():
    import os
    if os.path.exists('.progress'):
        os.remove('.progress')


def set_progress(p):
    with open('.progress', 'w+') as tmp_file:
        tmp_file.write(str(p))


def get_progres():
    with open('.progress', 'rw') as tmp_file:
        return tmp_file.read()


tmp_length = 0


def print_progress(message, value, size, prefix="", progress_style="#"):
    toolbar_width = 60

    def get_bar(percent):
        global tmp_length
        pro_count = int(percent * toolbar_width / 100)
        template = prefix + "[%s%s] %.1f%% %s/%s" % (progress_style * pro_count, " " * (toolbar_width - pro_count), percent, value, size)
        tmp_length = len(template)
        return template

    sys.stdout.write("\b" * tmp_length)  # return to start of line, after '['
    print(message + " " * tmp_length)
    sys.stdout.write(get_bar(value * 100.0 / size))
    sys.stdout.flush()
    if value == size:
        sys.stdout.write('\n')


if __name__ == "__main__":
    for i in range(80):
        print_progress("12", i + 1, 80)
    print(444444)
