from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk


class MailFrame(tk.Frame):
    def __init__(self, master=None, font=("Monospace", 45), cnf={}, **kw):
        super(MailFrame, self).__init__(master=master, cnf=cnf, **kw)

        self.__image_file = Image.open("server/GUI/icons/email.png").resize((60, 60),
                                                                            Image.ANTIALIAS)
        self.__mail_icon = ImageTk.PhotoImage(self.__image_file)

        self.__image = tk.Label(self, image=self.__mail_icon, width=60, height=60)
        self.__image.grid(row=0, sticky=tk.W)

        self.__count = tk.StringVar()
        self.__count.set("0")
        self.__count_label = tk.Label(self, textvariable=self.__count, font=font)
        self.__count_label.grid(row=1, sticky=tk.W)

    def update_count(self, count):
        count = int(count)
        if count > 9:
            self.__count.set("9+")
        else:
            self.__count.set(str(count))


class TimeFrame(tk.Frame):
    def __init__(self, master=None, time_font=("Monospace", 45), date_font=("Monospace",
                                                                            30), cnf={}, **kw):
        super(TimeFrame, self).__init__(master=master, cnf=cnf, **kw)

        self.__time_string = tk.StringVar()
        self.__time_string.set("00:00")
        self.__time = tk.Label(self, textvariable=self.__time_string, font=time_font)
        self.__time.grid(row=0)

        self.__date_string = tk.StringVar()
        self.__date_string.set("1970.01.01")
        self.__date = tk.Label(self, textvariable=self.__date_string, font=date_font)
        self.__date.grid(row=1)

    def update_date_time(self, time_string=None, date_sting=None):
        if time_string:
            self.__time_string.set(time_string)

        if date_sting:
            self.__date_string.set(date_sting)


class WeatherFrame(tk.Frame):
    def __init__(self, master=None, font=("Monospace", 45), temprature_unit="C",
                 cnf={}, **kw):
        super(WeatherFrame, self).__init__(master=master, cnf=cnf, **kw)

        self.DEGREE_SIGN = u'\N{DEGREE SIGN}'
        self.temp_unit = temprature_unit

        self.__temp_strig = tk.StringVar()
        self.__temp_strig.set("0 " + self.DEGREE_SIGN + self.temp_unit)

        self.__temp = tk.Label(self, textvariable=self.__temp_strig, font=font)
        self.__temp.grid(row=0)

        self.__city_strig = tk.StringVar()
        self.__city = tk.Label(self, textvariable=self.__city_strig, font=("Monospace", 30))
        self.__city.grid(row=1)

    def update_data(self, temperature=None, city=None):
        if temperature:
            self.__temp_strig.set(str(temperature) + " " + self.DEGREE_SIGN + self.temp_unit)

        if city:
            self.__city_strig.set(city)


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
