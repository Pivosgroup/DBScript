# -*- coding: utf-8 -*-
import sys
from pinyin_dict import pinyin_dict


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


if __name__ == "__main__":
    print_progress(12, 3, 4)
