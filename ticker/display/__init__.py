from dataclasses import dataclass


@dataclass
class DisplayItem:
    title: str = None
    message: str = ''
    wrap_line: bool = False
    iterations: int = 2
    time: int = 5


def scroll_text(text, iterations=2, width=15):
    if len(text) < width:
        return text
    for iteration in range(iterations):
        start_idx = 0
        final_idx = width
        while final_idx <= len(text):
            yield text[start_idx:final_idx]
            start_idx += 1
            final_idx += 1


def loop_text(text, width=15):
    while True:
        if text:
            for scrolled in scroll_text(text, iterations=1, width=width):
                yield scrolled
            yield ''
        else:
            yield ''


def zip_lines(top_text='', bottom_text='', iterations=2, width=15):
    if len(top_text) == len(bottom_text):
        return zip(
            scroll_text(top_text, iterations, width), scroll_text(bottom_text, iterations, width)
        )
    elif len(top_text) > len(bottom_text):
        return zip(
            scroll_text(top_text, iterations, width), loop_text(bottom_text, width)
        )
    elif len(top_text) < len(bottom_text):
        return zip(
            loop_text(top_text, width), scroll_text(bottom_text, iterations, width)
        )
