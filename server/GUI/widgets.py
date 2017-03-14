import tkinter as tk
from tkinter import ttk


class SlidingLabel(ttk.Label):
    def __init__(self, separator=u"\u00B7", master=None, text=None, delay=200,
                 font=("Helvetica", 50), **kw):
        """Construct a Ttk Label with parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, style, takefocus, text,
            textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            anchor, background, font, foreground, justify, padding,
            relief, text, wraplength
        :param separator: separator character for list items
        :param text: initial text (optional)
        :param font: text font. default is ("Helvetica", 50)
        :param delay: sleep time before sliding to next position in ms, default is 200ms
        """
        self.__str_var = tk.StringVar()
        super(SlidingLabel, self).__init__(master, font=font,
                                           textvariable=self.__str_var, **kw)
        self.separator = separator
        self.delay = delay  # wait time before sliding to next position, in ms
        self.text = text if text else ""
        self.__str_var.set(self.text)
        self.master.after(self.delay, self.__update_text_position)

    def __update_text_position(self):
        if len(self.text) > 1:
            self.text = self.text[1:] + self.text[0]
            self.__str_var.set(self.text)
            self.master.after(self.delay, self.__update_text_position)

    def load_lines(self, line_list):
        sep = " " + self.separator + " "
        txt = sep.join(line_list)
        txt += sep
        self.text = txt
        self.__str_var.set(self.text)
