import os
import tkinter as tk
import tkinter.filedialog as tkfd
from tkinter import messagebox
from language_strings import DE as M
import configparser

import win32api
import win32print


class Pen(tk.Frame):
    """ Create a Frame that holds the main application"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.mode = "window"
        self.cur_word = ""
        self.data = {}

        self.windows = {}
        self.cnf = configparser.ConfigParser()
        self.load_config()
        self.filename = self.cnf["FILE"]["last"]

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
            width=self.cnf["STYLE"]["width"],
            height=18
        )
        self.paper.bind("<KeyRelease>", self.auto_replace)
        self.paper.pack(fill=tk.Y, expand=1)
        self.config(bg=self.cnf["STYLE"]["bg"])

        self.show_menus()
        self.set_hotkeys()

        self.load_file()

    def show_menus(self):
        """ defines the menus ... """

        self.menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label=M.MENU_NEW, command=self.new_file)
        filemenu.add_command(label=M.MENU_OPEN, command=self.open_file)
        filemenu.add_command(label=M.MENU_SAVE, command=self.save_file)
        filemenu.add_command(label=M.MENU_SAVE_AS, command=self.save_as_dialog)
        filemenu.add_command(label=M.MENU_PREFS, command=self.show_prefs)
        filemenu.add_command(label=M.MENU_EXIT)
        self.menubar.add_cascade(label=M.MENU_FILE, menu=filemenu)
        self.parent.config(menu=self.menubar)

    def set_hotkeys(self):
        self.parent.bind("<Control-n>", self.new_file)
        self.parent.bind("<Control-s>", self.save_file)
        self.parent.bind("<Control-Shift-s>", self.save_as_dialog)
        self.parent.bind("<Control-+>", self.save_incremental)
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
        self.update_title()

    def open_file(self, event=None):
        self.filename = tkfd.askopenfilename()
        self.load_file()

    def load_file(self):
        if self.filename:
            try:
                file = open(self.filename, mode="rb")
                data = file.read()
                file.close()
                try:
                    decoded = data.decode("utf-8")
                except UnicodeDecodeError:
                    decoded = data.decode("cp1252")
            except FileNotFoundError:
                self.filename = "temp"
                decoded = ""
            self.paper.delete(0.0, tk.END)
            self.paper.insert(0.0, decoded)
            self.update_title()

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
            width=self.cnf["STYLE"]["width"],
            height=18
        )
        self.config(bg=self.cnf["STYLE"]["bg"])

    def update_title(self):
        if self.filename != "temp":
            self.parent.title(M.APP_NAME + " - " + self.filename)
        else:
            self.parent.title(M.APP_NAME)

    def save_file(self, event=None):
        if self.filename:
            self.data = self.paper.get(0.0, tk.END)
            with open(self.filename, mode="w", encoding="utf-8") as file:
                file.write(self.data)
                self.cnf["FILE"]["last"] = self.filename
                self.write_config()
                self.update_title()

    def save_as_dialog(self, event=None):
        self.filename = tkfd.asksaveasfilename()
        self.save_file(self)

    def save_incremental(self, event=None):
        name, ext = os.path.splitext(self.filename)
        name, num = os.path.splitext(name)
        if num:
            num = num[1::]
            num = int(num) + 1
            num = "." + str(num)
        else:
            num = ".1"
        new_filename = name + num + ext
        if (os.path.exists(new_filename)):
            messagebox.showerror(M.ERROR,M.E_FILE_EXISTS)
        else:
            self.filename = new_filename
            self.save_file()

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
        self.cnf["FILE"] = {
            "last": "temp"
        }
        self.cnf.read("config.ini")

    def write_config(self):
        with open("config.ini", mode="w", encoding="utf-8") as config_file:
            self.cnf.write(config_file)

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


