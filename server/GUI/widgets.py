import tkinter as tk
from tkinter import ttk


class SlidingLabel(ttk.Label):
    def __init__(self, separator=u"\u00B7", master=None, text=None, text_length=80, delay=150,
                 font=("Monospace", 50), **kw):
        """Construct a Ttk Label with parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, style, takefocus, text,
            textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            anchor, background, font, foreground, justify, padding,
            relief, text, wraplength
        :param separator: separator character for list items
        :param text: initial text (optional)
        :param text_length: length of visible text. widget only shows this number of characters
        at a time
        :param font: text font. default is ("Monospace", 50)
        :param delay: sleep time before sliding to next position in ms, default is 150ms
        """
        self.__str_var = tk.StringVar()
        super(SlidingLabel, self).__init__(master, font=font,
                                           textvariable=self.__str_var, **kw)
        self.separator = separator
        self.delay = delay  # wait time before sliding to next position, in ms
        self.text = text if text else ""
        self.text_len = text_length
        self.__str_var.set(self.text)
        self.master.after(self.delay, self.__update_text_position)

    def __update_ui(self):
        if len(self.text) < self.text_len:
            __diff = self.text_len - len(self.text)
            __half_diff = int((__diff + 0.5) / 2)
            self.text = (" " * __half_diff) + self.text + (" " * __half_diff)
        self.__str_var.set(self.text[0:self.text_len])

    def __update_text_position(self):
        if len(self.text) > 1:
            self.text = self.text[1:] + self.text[0]
            self.__update_ui()
            self.master.after(self.delay, self.__update_text_position)

    def load_lines(self, line_list):
        sep = " " + self.separator + " " if (len(line_list) > 1) else " "
        txt = " " + sep.join(line_list)
        txt += sep
        self.text = txt
        self.__update_ui()
