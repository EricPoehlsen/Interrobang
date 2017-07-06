import tkinter as tk
import tkinter.font as tkfont
import tkinter.filedialog as tkfd
import tkinter.colorchooser as tkcolor
from language_strings import DE as M
import configparser
import re

# print
import tempfile
import win32api
import win32print

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
        size_frame = tk.LabelFrame(frame, text=M.PREFS_SIZE)
        self.data["fg_entry"] = tk.Entry(size_frame, textvariable=self.data["size"])
        self.data["fg_entry"].pack()
        size_frame.pack()

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
        self.data["size"].set(int(self.cnf["STYLE"]["size"]))
        self.data["fg"].set(self.cnf["STYLE"]["fg"])
        self.data["bg"].set(self.cnf["STYLE"]["bg"])

    def get_fonts(self):
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


class Pen(tk.Frame):
    """ Create a Frame that holds the main application"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mode = "window"
        self.filename = "temp"
        self.cur_word = ""
        self.data = {}

        self.windows = {}
        self.cnf = configparser.ConfigParser()
        self.load_config()

        self.paper = tk.Text(self, wrap=tk.WORD)
        font = (
            self.cnf["STYLE"]["font"],
            self.cnf["STYLE"]["size"],
            ""
        )
        self.paper.config(
            bg=self.cnf["STYLE"]["bg"],
            insertbackground=self.cnf["STYLE"]["fg"],
            fg=self.cnf["STYLE"]["fg"],
            border=0,
            font=font,
            width=48,
            height=18
        )
        self.paper.bind("<KeyRelease>", self.auto_replace)
        self.paper.pack(fill=tk.Y, expand=1)
        self.config(bg=self.cnf["STYLE"]["bg"])

        self.show_menus()
        self.set_hotkeys()

    def show_menus(self):
        """ defines the menus ... """

        self.menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label=M.MENU_NEW, command=self.new_file)
        filemenu.add_command(label=M.MENU_OPEN, command=self.open_file)
        filemenu.add_command(label=M.MENU_SAVE, command=self.save_file)
        filemenu.add_command(label=M.MENU_PREFS, command=self.show_prefs)
        filemenu.add_command(label=M.MENU_EXIT)
        self.menubar.add_cascade(label=M.MENU_FILE, menu=filemenu)
        self.parent.config(menu=self.menubar)

    def set_hotkeys(self):
        self.parent.bind("<Control-n>", self.new_file)
        self.parent.bind("<Control-s>", self.save_file)
        self.parent.bind("<Control-o>", self.open_file)
        self.parent.bind("<Control-f>", self.show_searchbox)
        self.parent.bind("<Control-p>", self.printer)
        self.parent.bind("<F3>", lambda e: self.goto("next"))
        self.parent.bind("<Shift-F3>", lambda e: self.goto("prev"))
        self.parent.bind("<F11>", self.toggle_full_screen)

    def show_prefs(self):
        """ Display a preferences window"""

        if not self.windows.get("prefs"):
            self.windows["prefs"] = Preferences(self)
        else:
            self.windows["prefs"].focus()

    def new_file(self, event=None):
        self.paper.delete(0.0,tk.END)
        self.filename = "temp"

    def open_file(self, event=None):
        self.filename = tkfd.askopenfilename()
        if self.filename:
            file = open(self.filename, mode="rb")
            data = file.read()
            file.close()

            try:
                decoded = data.decode("utf-8")
            except UnicodeDecodeError:
                decoded = data.decode("cp1252")

            self.paper.delete(0.0,tk.END)
            self.paper.insert(0.0, decoded)

    def update_view(self):
        font = (
            self.cnf["STYLE"]["font"],
            self.cnf["STYLE"]["size"],
            ""
        )
        self.paper.config(
            bg=self.cnf["STYLE"]["bg"],
            insertbackground=self.cnf["STYLE"]["fg"],
            fg=self.cnf["STYLE"]["fg"],
            border=0,
            font=font,
            width=48,
            height=18
        )
        self.config(bg=self.cnf["STYLE"]["bg"])


    def save_file(self, event=None):
        self.filename = tkfd.asksaveasfilename()
        if self.filename:
            self.data = self.paper.get(0.0, tk.END)
            file = open(self.filename, mode="w", encoding="utf-8")
            file.write(self.data)
            file.close()

    def load_config(self):
        self.cnf.sections()
        self.cnf["CORE"] = {"geometry": ""}
        self.cnf["STYLE"] = {
            "fg": "#000000",
            "bg": "#ffffff",
            "font": "Arial",
            "bold": "0",
            "italic": "0",
            "size": "12",
            "width": "60"
        }
        self.cnf.read("config.ini")

    def toggle_full_screen(self, event=None):
        """ switch between fullscreen and window mode """

        if self.mode == "window":
            self.menubar.delete(0, tk.END)
            self.cnf["CORE"]["geometry"] = self.parent.geometry()
            self.parent.wm_attributes('-fullscreen','true')
            self.mode = "fullscreen"
        else:
            self.parent.wm_attributes('-fullscreen', 'false')
            self.show_menus()
            self.parent.geometry(self.cnf["CORE"]["geometry"])
            self.mode = "window"

    def show_searchbox(self, event=None):
        box = tk.Toplevel(self)
        box.title(M.SEARCH_TITLE)
        x = int(self.winfo_rootx() + (self.winfo_width() / 2) - 100)
        y = int(self.winfo_rooty() + (self.winfo_height() / 2) - 20)
        box.geometry("200x40+{x}+{y}".format(x=x, y=y))
        entry = tk.Entry(box)
        entry.bind("<Return>", self.find_all)
        self.data["search"] = tk.StringVar()
        entry.config(textvariable=self.data["search"])
        entry.pack(fill=tk.BOTH, expand=1)
        entry.focus()

    def find_all(self, event=None):
        """ Finds all occurrences of the current search term"""
        if self.data.get("search"):
            search = self.data["search"].get()
        else:
            search = ""

        if event:
            toplevel = event.widget.winfo_toplevel()
            toplevel.destroy()

        text = self.paper.get(0.0, tk.END)
        if self.data.get("case_insensitive", True):
            search = search.lower()
            text = text.lower()

        text = text.split("\n")
        places = []
        for i, line in enumerate(text, start=1):
            n = 0
            while line.find(search, n) > -1:
                n = line.find(search, n)
                places.append("{i}.{n}".format(i=i, n=n))
                n += 1
                if n >= len(line): break
        self.data["result"] = places
        print(places)
        self.paper.focus()
        self.goto("next")

    def goto(self, mode):
        """ jump to next or previous search result """
        cur_index = self.paper.index(tk.INSERT)
        prev = next = 0
        if self.data["result"]:
            for i, index in enumerate(self.data["result"]):
                if float(index) > float(cur_index):
                    if len(self.data["result"]) > 1:
                        prev = i - 1
                    else: prev = i
                    next = i
                    break

            # go back if currently on a marker ...
            if self.data["result"][prev] == cur_index:
                if i > 1:
                    prev -= 1
                else:
                    prev = len(self.data["result"]) - 1

            print(
                "pos", cur_index,
                "prev", self.data["result"][prev],
                "next", self.data["result"][next]
            )
            if mode == "prev":
                self.paper.mark_set(tk.INSERT, self.data["result"][prev])

            if mode == "next":
                self.paper.mark_set(tk.INSERT, self.data["result"][next])

            self.paper.see(tk.INSERT)

    def auto_replace(self, event):
        """ replaces specific text combination on input """

        if event.keysym in ["space", "Return", "BackSpace"]:
            self.cur_word = ""
        else: self.cur_word += event.char

        if self.cur_word == '"':
            line, pos = self.paper.index(tk.INSERT).split(".")
            pos = int(pos)

            first = line + "." + str(pos-1)
            last = line + "." + str(pos)

            self.paper.delete(first, last)
            self.paper.insert(first, "»")
            self.cur_word = ""
        elif self.cur_word.endswith('"'):
            line, pos = self.paper.index(tk.INSERT).split(".")
            pos = int(pos)

            first = line + "." + str(pos-1)
            last = line + "." + str(pos)

            self.paper.delete(first, last)
            self.paper.insert(first, "«")
            self.cur_word = ""

        if self.cur_word == "'":
            line, pos = self.paper.index(tk.INSERT).split(".")
            pos = int(pos)

            first = line + "." + str(pos-1)
            last = line + "." + str(pos)

            self.paper.delete(first, last)
            self.paper.insert(first, "›")
            self.cur_word = ""
        elif self.cur_word.endswith("'"):
            line, pos = self.paper.index(tk.INSERT).split(".")
            pos = int(pos)

            first = line + "." + str(pos-1)
            last = line + "." + str(pos)

            self.paper.delete(first, last)
            self.paper.insert(first, "‹")
            self.cur_word = ""

        if len(self.cur_word) > 1 and self.cur_word.endswith("!"):
            if self.cur_word[-2] == "?":
                line, pos = self.paper.index(tk.INSERT).split(".")
                pos = int(pos)

                first = line + "." + str(pos - 2)
                last = line + "." + str(pos)

                self.paper.delete(first, last)
                self.paper.insert(first, "‽")
                self.cur_word = "."

        if len(self.cur_word) > 1 and self.cur_word.endswith("-"):
            if self.cur_word[-2] == "-":
                line, pos = self.paper.index(tk.INSERT).split(".")
                pos = int(pos)

                first = line + "." + str(pos - 2)
                last = line + "." + str(pos)

                self.paper.delete(first, last)
                self.paper.insert(first, "–")

    def printer(self, event=None):
        pass

if __name__ == '__main__':
    window = tk.Tk()
    app = Pen(window)
    app.pack(fill=tk.BOTH, expand=1)
    window.mainloop()