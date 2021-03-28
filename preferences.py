import tkinter as tk
import tkinter.font as tkfont
import tkinter.colorchooser as tkcolor
from language_strings import DE as M
import re


class Preferences(tk.Toplevel):
    """ Create a top level widget to set the program preferences """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.cnf = parent.cnf
        self.data = {}


        self.font_frame = tk.Frame(self)
        list_frame = tk.LabelFrame(self.font_frame, text=M.PREFS_FONTS)
        self.font_entry = tk.Entry(list_frame, width=30)
        self.font_entry.pack(fill=tk.X)
        self.font_entry.bind("<KeyRelease>", self.filter_fonts)
        self.list = tk.Listbox(list_frame)
        self.list.bind("<<ListboxSelect>>", self.font_selected)
        self.list.pack(fill=tk.BOTH)
        list_frame.pack(side=tk.LEFT)

        self.data["width"] = tk.StringVar()
        self.data["bold"] = tk.IntVar()
        self.data["bold"].trace("w", lambda n, e, m: self.set_font())
        self.data["italic"] = tk.IntVar()
        self.data["italic"].trace("w", lambda n, e, m: self.set_font())
        self.data["size"] = tk.IntVar()
        self.data["size"].trace("w", lambda n, e, m: self.set_font())
        self.data["fg"] = tk.StringVar()
        self.data["fg"].trace("w", lambda n, e, m: self.set_color("fg"))
        self.data["bg"] = tk.StringVar()
        self.data["bg"].trace("w", lambda n, e, m: self.set_color("bg"))

        frame = tk.Frame(self.font_frame)


        width_frame = tk.LabelFrame(frame, text=M.PREFS_WIDTH)
        self.data["width_entry"] = tk.Entry(width_frame, textvariable=self.data["width"])
        self.data["width_entry"].pack(fill=tk.X)
        width_frame.pack(fill=tk.X)

        size_frame = tk.LabelFrame(frame, text=M.PREFS_SIZE)
        self.data["size_entry"] = tk.Entry(size_frame, textvariable=self.data["size"])
        self.data["size_entry"].pack(fill=tk.X)
        size_frame.pack(fill=tk.X)

        bold = tk.Checkbutton(frame, variable=self.data["bold"], text=M.PREFS_BOLD)
        bold.pack()
        italic = tk.Checkbutton(frame, variable=self.data["italic"], text=M.PREFS_ITALIC)
        italic.pack()

        fg_frame = tk.LabelFrame(frame, text=M.PREFS_FG)
        self.data["fg_entry"] = tk.Entry(fg_frame, textvariable=self.data["fg"])
        self.data["fg_entry"].pack(fill=tk.BOTH, side=tk.LEFT)
        fg_button = tk.Button(
            fg_frame,
            text=M.PREFS_DOTS,
            command=lambda:self.color_selector("fg")
        )
        fg_button.pack(side=tk.LEFT)
        fg_frame.pack()

        bg_frame = tk.LabelFrame(frame, text=M.PREFS_BG)
        self.data["bg_entry"] = tk.Entry(bg_frame, textvariable=self.data["bg"])
        self.data["bg_entry"].pack(fill=tk.BOTH, side=tk.LEFT)
        bg_button = tk.Button(
            bg_frame,
            text=M.PREFS_DOTS,
            command=lambda:self.color_selector("bg")
        )
        bg_button.pack(side=tk.LEFT)
        bg_frame.pack()
        frame.pack(side=tk.LEFT)

        self.font_frame.pack()

        # test display
        self.test_entry = tk.Entry(self, width=1)
        self.test_entry.insert(0, M.PREFS_TEST)
        self.test_entry.pack(fill=tk.BOTH)

        # the buttons
        self.save = tk.Button(self, text=M.PREFS_OK, command=self.save)
        self.cancel = tk.Button(self, text=M.PREFS_CANCEL)
        self.save.pack(fill=tk.X)
        self.cancel.pack(fill=tk.X)
        self.get_fonts()

        # load current values
        self.data["bold"].set(int(self.cnf["STYLE"]["bold"]))
        self.data["italic"].set(int(self.cnf["STYLE"]["italic"]))
        self.data["width"].set(int(self.cnf["STYLE"]["width"]))
        self.data["size"].set(int(self.cnf["STYLE"]["size"]))
        self.data["fg"].set(self.cnf["STYLE"]["fg"])
        self.data["bg"].set(self.cnf["STYLE"]["bg"])

    def get_fonts(self):
        """ retrieves available fonts using tk """
        self.data["fonts"] = tkfont.families()
        self.data["fonts"] = sorted(self.data["fonts"])
        self.list.insert(0, *self.data["fonts"])

    def filter_fonts(self, event):
        """ Filter fonts based on text field """
        search = event.widget.get()
        fonts = self.data["fonts"]
        fonts = [f for f in fonts if search.lower() in f.lower()]
        self.list.delete(0, tk.END)
        self.list.insert(0, *fonts)

    def color_selector(self, var):
        """ calls the colorpicker and sets the appropriate color variable """
        color = tkcolor.askcolor(parent=self, initialcolor=self.data[var].get() )
        if color[1]:
            self.data[var].set(color[1])

    def set_color(self, var):
        """ updates the display colors when the color variable is changed """
        if var not in ["fg", "bg"]: return

        value = self.data[var].get()
        if re.match("^#[0-9a-f]{6}$", value):
            r = int(value[1:3], 16)
            g = int(value[3:5], 16)
            b = int(value[5:], 16)

            # make sure it is readable
            if (r+g+b)/3 < 128: fg = "#ffffff"
            else: fg = "#000000"

            self.data[var+"_entry"].config(
                fg=fg,
                bg=value
            )

            if var == "fg":
                self.test_entry.config(fg=value)
            if var == "bg":
                self.test_entry.config(bg=value)

        # reset to black on white
        else:
            self.data[var + "_entry"].config(
                fg = "#000000",
                bg = "#ffffff"
            )

    def set_font(self):
        """ set font and size in demo field """
        size = 0
        if self.data.get("size"):
            try:
                size = self.data["size"].get()
            except tk.TclError:
                size = 0
            if int(size) > 100: size = 0
        if not size: size = 12

        if self.data.get("font_family"):
            family = self.data["font_family"]
            self.font_entry.delete(0,tk.END)
            self.font_entry.insert(0,family)
        else:
            family = "Arial"

        self.test_entry.config(font=(family, size, ""))

    def font_selected(self, event):
        """ The user has just selected a font """
        index = self.list.curselection()
        if index:
            value = self.list.get(index)
            self.data["font_family"] = value
            self.set_font()

    def save(self):
        """ recheck all values and write the config """
        width = int(self.data["width"].get())
        if width > 0:
            self.cnf["STYLE"]["width"] = str(width)

        size = int(self.data["size"].get())
        if 0 < size < 100:
            self.cnf["STYLE"]["size"] = str(self.data["size"].get())

        if self.data.get("font_family"):
            self.cnf["STYLE"]["font"] = self.data["font_family"]

        for col in ["fg", "bg"]:
            if self.data.get(col):
                value = self.data[col].get()
            else: value = ""
            if re.match("^#[0-9a-f]{6}$", value):
                self.cnf["STYLE"][col] = value

        for extra in ["bold", "italic"]:
            self.cnf["STYLE"][extra] = str(self.data[extra].get())

        with open("config.ini", mode="w", encoding="utf-8") as file:
            self.cnf.write(file)

        self.parent.update_view()

    def close(self):
        self.parent.windows["prefs"] = None
        self.destroy()