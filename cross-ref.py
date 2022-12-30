#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2022-Present, Miguel A. Guerrero
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Please send bugs and suggestions to: miguel.a.guerrero@gmail.com
# -------------------------------------------------------------------------------

import os
import sys
import tkinter as tk
from tkinter import filedialog
from enum import IntEnum


class PANE(IntEnum):
    left = 0
    right = 1


class LabelsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.left_label = tk.Label(self, text="Left File")
        self.left_label.pack(side="left", fill="x")
        self.right_label = tk.Label(self, text="Right File")
        self.right_label.pack(side="right", fill="x")


class TextViewer(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # add a flag to track whether the cross-reference file has been loaded
        self.cross_ref_loaded = False

        # add a status label
        self.status_label = tk.Label(self, text="Cross-reference: not loaded")
        self.status_label.pack(side="bottom")

        # add a container for the file names
        self.file_labels = LabelsFrame(self)
        self.file_labels.pack(side="top", fill="x")

        # add left and right text pannels
        self.left_text = tk.Text(self, width=80, height=40)
        self.left_text.pack(side="left", fill="both", expand=True)
        self.right_text = tk.Text(self, width=80, height=40)
        self.right_text.pack(side="right", fill="both", expand=True)

        self.left_text.tag_configure("highlight", background="dark green")
        self.right_text.tag_configure("highlight", background="dark green")

        self.left_text.bind("<Button-1>", self.on_left_click)
        self.right_text.bind("<Button-1>", self.on_right_click)

        self.file_line_cnt = [0, 0]
        self.group_by_line = [{}, {}]
        self.lines_by_group = [[], []]

    def on_left_click(self, event):
        line_num = int(
            self.left_text.index("@%s,%s" % (event.x, event.y)).split(".")[0]
        )
        group = self.group_by_line[PANE.left].get(line_num)
        self.highlight_line(
            group,
            self.left_text,
            self.right_text,
            self.lines_by_group[PANE.left],
            self.lines_by_group[PANE.right],
        )

    def on_right_click(self, event):
        line_num = int(
            self.right_text.index("@%s,%s" % (event.x, event.y)).split(".")[0]
        )
        group = self.group_by_line[PANE.right].get(line_num)
        self.highlight_line(
            group,
            self.right_text,
            self.left_text,
            self.lines_by_group[PANE.right],
            self.lines_by_group[PANE.left],
        )

    def highlight_line(
        self,
        group,
        source_widget,
        target_widget,
        source_lines_by_group,
        target_lines_by_group,
    ):
        def hilight_range(line_nums, widget, scroll):
            for line_num in line_nums:
                # scroll the target widget so that the highlighted line is visible
                if scroll:
                    widget.see(f"{line_num}.0")
                widget.tag_add(
                    "highlight",
                    f"{line_num}.0",
                    f"{line_num}.end",
                )

        source_widget.tag_remove("highlight", "1.0", "end")
        target_widget.tag_remove("highlight", "1.0", "end")

        if group is not None:
            target_line_nums = target_lines_by_group[group]
            hilight_range(target_line_nums, target_widget, scroll=True)
            source_line_nums = source_lines_by_group[group]
            hilight_range(source_line_nums, source_widget, scroll=False)

    def load_left_file(self, filepath=None):
        if filepath is None:
            filepath = filedialog.askopenfilename(initialdir=os.getcwd())
        if filepath != "":
            self.file_line_cnt[PANE.left] = TextViewer.fill_with_file(
                self.left_text, filepath
            )
            self.file_labels.left_label.configure(text=filepath)

    def load_right_file(self, filepath=None):
        if filepath is None:
            filepath = filedialog.askopenfilename()
        if filepath != "":
            self.file_line_cnt[PANE.right] = TextViewer.fill_with_file(
                self.right_text, filepath
            )
            self.file_labels.right_label.configure(text=filepath)

    @staticmethod
    def fill_with_file(text, filepath):
        with open(filepath, "r") as f:
            lines = f.readlines()
            lines = ["%4d: %s" % (i, line) for i, line in enumerate(lines, 1)]
            text.delete("1.0", "end")
            text.insert("1.0", "".join(lines))
        text.configure(state="disabled")  # make the widget read-only
        return len(lines)

    @staticmethod
    def fill_line_nums(curr_part, lowest_nxt):
        # expand a line range with format: a  | a-b | a-
        # into a list of integers
        def line_nums_from_range(rng, implicit_end):
            if "-" not in rng:
                return [int(rng)]
            parts = rng.split("-")
            if len(parts) > 2:
                raise f"Incorrect format for a-b range, too many - in: {rng}"
            a = int(parts[0])
            b = int(parts[1]) if parts[1].strip() != "" else implicit_end
            return [i for i in range(a, b + 1)]

        # could have any number of ranges separated by commas, expand them
        line_nums = []
        for rng in curr_part.split(","):
            line_nums += line_nums_from_range(rng, lowest_nxt - 1)
        return line_nums

    def load_cross_ref(self, filepath=None):

        if filepath is None:
            if (
                self.file_line_cnt[PANE.left] == 0
                or self.file_line_cnt[PANE.right] == 0
            ):
                tk.messagebox.showerror(
                    "Error", "leff & right files must be non-empty"
                )
                return
            filepath = filedialog.askopenfilename()
        if filepath is not None:
            with open(filepath, "r") as f:
                lines = f.readlines()

        # process the file once for left side references, once for right side
        for left_right in range(2):
            # choose the right data structures to fill-ip (left vs right)
            group_by_line = self.group_by_line[left_right]
            lines_by_group = self.lines_by_group[left_right]
            file_line_cnt = self.file_line_cnt[left_right]

            group = 0
            # this is used for open intervals. E.g. a-
            # the right handnd side is assumed next groups beginning - 1
            nxt_group_lowest_line_no = file_line_cnt + 1
            for line in reversed(lines):
                # choose left or right side of the : divider
                part = line.strip().split(":")[left_right]
                # expand into line numbers
                line_nums = TextViewer.fill_line_nums(
                    part, nxt_group_lowest_line_no
                )
                # fill-up the mapping from line number to group
                for line_num in line_nums:
                    group_by_line[line_num] = group
                # and from group to line numbers
                lines_by_group.append(line_nums)
                # the minimum line number of this group is used to derive the limit
                # of the previous (its next)
                nxt_group_lowest_line_no = min(line_nums)
                group += 1

        # update the flag to indicate that the cross-reference file has been loaded
        self.cross_ref_loaded = True
        # update the status label
        self.status_label.configure(text=f"Cross-reference: {filepath}")


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Croos-Reference between two files")
        self.text_viewer = TextViewer(self)
        self.text_viewer.pack(side="top", fill="both", expand=True)

        tk.Button(
            self,
            text="Load Left File",
            command=self.text_viewer.load_left_file,
        ).pack(side="left")
        tk.Button(
            self,
            text="Load Right File",
            command=self.text_viewer.load_right_file,
        ).pack(side="left")
        tk.Button(
            self,
            text="Load Cross-Reference",
            command=self.text_viewer.load_cross_ref,
        ).pack(side="left")
        tk.Button(
            self,
            text="Quit",
            command=self.destroy,
        ).pack(side="right")


if __name__ == "__main__":
    app = MainWindow()

    if len(sys.argv) > 1:
        app.text_viewer.load_left_file(sys.argv[1])
        if len(sys.argv) > 2:
            app.text_viewer.load_right_file(sys.argv[2])
            if len(sys.argv) > 3:
                app.text_viewer.load_cross_ref(sys.argv[3])
    else:
        # informative, GUI gets opened anyways
        print(
            "\nCommand line Usage:\n"
            f"{sys.argv[0]} [leftFile [rightFile [crossRef]]]\n"
        )
        print(
            "\nLoad left file, right file and then cross-reference file."
            "\nClick any line on any pane to see corresponding lines"
            "\nhighlighed on the other pane."
        )

    app.mainloop()
