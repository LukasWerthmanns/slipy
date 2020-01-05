#!/usr/bin/python3
import os
# import time
import curses
import subprocess
from curses.textpad import Textbox, rectangle
from builtins import (FileExistsError,
                      IsADirectoryError,
                      FileNotFoundError)
from MarkedEntry import MarkedDirContents
import shutil
# NotADirectoryError)
# import tempfile

# todo
# n goes to next directory, b goes back
# search option
# command prompt


class Frame:
    def __init__(self, cwd, dir_contents, stdscr, sxiv_pid=0,
                 marked=[], curr_top=0, curr_pos=0,
                 curr_pos_entries=[], curr_top_entries=[]):
        self.music_icon = "/home/user/python/slipy/music_icon.png"
        self.stdscr = stdscr
        self.cwd = cwd
        self.dir_contents = dir_contents
        self.rows, self.columns = stdscr.getmaxyx()
        self.curr_top = curr_top
        self.curr_pos = curr_pos
        self.bottom_offset = (self.rows - 3)
        self.max_pos = len(dir_contents)-1
        self.sxiv_pid = sxiv_pid
        self.tmpfile = "/tmp/slipy/"
        self.deleted = self.tmpfile + "deleted/"
        self.marked = marked
        self.color_normal = 0
        self.color_current = 1
        self.color_current_marked = 2
        self.color_marked = 3
        self.color_directory = 4
        self.color_current_directory = 5
        self.curr_pos_entries = curr_pos_entries
        self.curr_top_entries = curr_top_entries
        self.dir_depth = cwd.count("/")
        if self.curr_pos_entries == []:
            self.curr_pos_entries = [0]*(self.dir_depth + 1)
        if self.curr_top_entries == []:
            self.curr_top_entries = [0]*(self.dir_depth + 1)
        self.max_dir_depth = len(self.curr_pos_entries) - 1
        # self.curr_pos_entries[self.dir_depth] = curr_pos

    def get_from_line(self, prompt_string):
        curses.echo()
        self.stdscr.addstr(self.bottom_offset + 1, 0, prompt_string +
                           " " * (self.columns - len(prompt_string)))
        self.stdscr.refresh()
        input = self.stdscr.getstr(self.bottom_offset +
                                   2, 0, 20).decode("utf-8")
        self.stdscr.addstr(self.bottom_offset + 2, 0, " " * (self.columns - 1))
        curses.noecho()
        return input

    def console(self):
        curses.echo()
        self.stdscr.addstr(self.bottom_offset + 2, 0, ":" +
                           " "*(self.columns - 2))
        self.stdscr.refresh()
        input = self.stdscr.getstr(self.bottom_offset +
                                   2, 1, self.columns - 3).decode("utf-8")
        self.stdscr.addstr(self.bottom_offset + 2, 0, " " * (self.columns - 1))
        curses.noecho()
        if input == "":
            return
        inputlist = input.split()
        if inputlist[0] == "mkdir" or inputlist[0] == "m":
            self.create_file("d", str(inputlist[1]))
        if inputlist[0] == "touch" or inputlist[0] == "t":
            self.create_file("t", str(inputlist[1]))
        if ((inputlist[0] == "delete" and inputlist[1] == "marked")
           or inputlist[0] == "DM"):
            self.delete_marked()
        if ((inputlist[0] == "move" and inputlist[1] == "marked")
           or inputlist[0] == "MM"):
            self.move_marked()
        if (inputlist[0] == "q"):
            exit()

# only one level at a time
    def change_dir(self, path):
        self.curr_pos_entries[self.dir_depth] = self.curr_pos
        self.curr_top_entries[self.dir_depth] = self.curr_top
        os.chdir(path)
        new_cwd = os.getcwd()

        new_depth = self.get_dir_depth(new_cwd)
        if new_depth > self.max_dir_depth:
            self.curr_pos_entries.append(0)
            self.curr_top_entries.append(0)
            self.max_dir_depth += 1
        if new_depth > self.dir_depth:
            self.curr_pos_entries[new_depth] = 0
            self.curr_top_entries[new_depth] = 0
            self.curr_pos = 0
            self.dir_depth += 1
        else:
            self.curr_pos = self.curr_pos_entries[new_depth]
            self.curr_top = self.curr_top_entries[new_depth]
            self.dir_depth -= 1
        self.reload_dir()
        new_dir_content = os.listdir(new_cwd)
        self.__init__(new_cwd, new_dir_content, self.stdscr,
                      self.sxiv_pid, self.marked,
                      self.curr_top_entries[self.dir_depth],
                      self.curr_pos_entries[self.dir_depth],
                      self.curr_pos_entries, self.curr_top_entries)
        self.stdscr.clear()
        self.print_contents()
        # self.print_contents(str(self.curr_pos_entries[self.dir_depth]) +
        #                     " " +
        #                     str(self.curr_top_entries[self.dir_depth]))

    def reload_dir(self):
        self.dir_contents = os.listdir(self.cwd)
        # dir_contents = os.listdir(self.cwd)
        self.max_pos = len(self.dir_contents)-1
        if self.curr_pos > self.max_pos:
            self.curr_pos = self.max_pos

    def resize(self):
        self.rows, self.columns = self.stdscr.getmaxyx()
        self.bottom_offset = (self.rows - 3)
        new_top = self.curr_pos - self.bottom_offset//2
        if new_top < 0:
            new_top = 0
        self.curr_top = new_top
        self.stdscr.clear()
        self.print_contents()

    # returns object with current cwd or None
    def cwd_in_marked_list(self):
        if self.marked != []:
            for marked_entry in self.marked:
                if marked_entry.dir_location == self.cwd:
                    return marked_entry
            return None
        else:
            return None

# Toggle mark on element
# Store all marked elements for the their respective cwds
# in a MarkedDirContents Object and thes objects in the
# self.marked list
    def mark(self, file):
        mark_obj = self.cwd_in_marked_list()
        if mark_obj is None:
            cwd = self.cwd
            mark_obj = MarkedDirContents(cwd)
            self.marked.append(mark_obj)
        # mark_obj.add_element(file)
        mark_obj.toggle_element(file)
        # self.stdscr.clear()
        # self.print_stuff()
        self.print_contents()

    def mark_mode(self):
        self.mark(self.dir_contents[self.curr_pos])
        self.print_contents("Mark mode: press \"V\" to quit")
        while True:
            key = self.stdscr.getch()
            if chr(key) == "V":
                self.print_contents("Mark mode ended")
                break
            if chr(key) == "j":
                self.move_cursor(1)
                self.mark(self.dir_contents[self.curr_pos])
            if chr(key) == "k":
                self.move_cursor(-1)
                self.mark(self.dir_contents[self.curr_pos])
            else:
                self.print_contents("Mark mode: press \"V\" to quit")

    def print_stuff(self, message=""):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, str(message) + " <- message")
        try:
            self.stdscr.addstr(1, 0, str(self.marked[0].dir_location))
            self.stdscr.addstr(2, 0, str(self.marked[0].marked_entries))
            self.stdscr.addstr(3, 0, str(self.marked[1].dir_location))
            self.stdscr.addstr(4, 0, str(self.marked[1].marked_entries))
            self.stdscr.addstr(5, 0, str(self.marked[2].dir_location))
            self.stdscr.addstr(6, 0, str(self.marked[2].marked_entries))
        except IndexError:
            print("")
        # self.stdscr.addstr(3, 0, str("curr_top:" + str(self.curr_top)))
        # self.stdscr.addstr(4, 0, str("max_pos: " + str(self.max_pos)))
        self.stdscr.refresh()
        # time.sleep(1)
        # self.print_contents()
        # exit()

    # prints everything from curr_top to
    # curr_top + bottom_offset
    # message will be displayed at the second last line
    # directories and entries in objects in marked list will be
    # higlighted accordingly
    def print_contents(self, message=""):
        i = 0
        while i < self.bottom_offset:
            top_plus_i = self.curr_top + i
            if top_plus_i > (self.max_pos):
                break
            current_element = self.dir_contents[top_plus_i]
            # Set Entry to print
            line_content_start = ((str(top_plus_i) + ": " +
                                   current_element)[:self.columns - 4])
            content_start_length = len(line_content_start)
            line_content_end = (self.columns - content_start_length) * ' '
            # Set colors
            mark_obj = self.cwd_in_marked_list()
            if top_plus_i == self.curr_pos:
                if (not(mark_obj is None) and
                   mark_obj.id_of_element(current_element) >= 0):
                    color = self.color_current_marked
                # if any(current_element in sublist for sublist in
                #         self.marked):
                #     color = self.color_current_marked
                elif os.path.isdir(current_element):
                    color = self.color_current_directory
                else:
                    color = self.color_current
            else:
                # mark_obj = self.cwd_in_marked_list()
                if (not(mark_obj is None) and
                   mark_obj.id_of_element(current_element) >= 0):
                    color = self.color_marked
                # if any(current_element in sublist for sublist in
                #         self.marked):
                #     color = self.color_marked
                elif os.path.isdir(current_element):
                    color = self.color_directory
                else:
                    color = self.color_normal
            # Print element
            self.stdscr.attron(curses.color_pair(color))
            self.stdscr.addstr(i, 0, line_content_start)
            self.stdscr.attroff(curses.color_pair(color))
            self.stdscr.addstr(i, content_start_length, line_content_end)
            i += 1
        # Print Message
        if message == "":
            message = self.cwd
            # message = str(self.curr_pos_entries) + str(self.dir_depth)
        message_end_string = message + " " * (self.columns - len(message))
        self.stdscr.addstr(self.rows - 2, 0, message_end_string)
        self.stdscr.refresh()

    # create 32 character textbox
    # return user input upon Ctrl-q or Enter
    # display message 1 at the top and message 2 at the bottom
    def get_from_box(self, message1="", message2=""):
        editwin = curses.newwin(1, 32, self.bottom_offset + 1, 1)
        rectangle(self.stdscr, self.bottom_offset, 0,
                  self.bottom_offset + 2, 1+31+1)
        self.stdscr.addstr(self.bottom_offset + 1, 1, " "*32)
        self.stdscr.addstr(self.bottom_offset, 0,
                           message1 + ":")
        self.stdscr.addstr(self.bottom_offset + 2, 0,
                           message2)
        self.stdscr.refresh()
        box = Textbox(editwin)
        box.edit()
        message = box.gather().strip()
        self.stdscr.clear()
        return message

    # creates textfile or directory when given "t" or "d" as
    # arguments
    # invokes promt for name
    def create_file(self, type, name=""):
        if type == "t":
            type_name = "textfile"
        elif type == "d":
            type_name = "directory"

        if name == "":
            filename = self.get_from_box("Enter name for " + type_name)
        else:
            filename = name
        if filename != "":
            try:
                if type == "t":
                    if filename not in self.dir_contents:
                        open(filename, 'w').close()
                    else:
                        raise FileExistsError
                if type == "d":
                    os.mkdir(filename)
                self.reload_dir()
                created_index = self.dir_contents.index(filename)
                self.dir_contents.insert(self.curr_pos,
                                         self.dir_contents.pop(created_index))
                self.print_contents("added " + filename + " at " +
                                    str(created_index))
            except FileExistsError:
                self.print_contents(filename + " exists")
            except IsADirectoryError:
                self.print_contents(filename + " exists and is a directory")
        else:
            self.print_contents()

    def delete_file(self, file):
        self.reload_dir()
        try:
            os.rename(file, os.path.join(self.deleted, file))
        except FileNotFoundError:
            return
        except OSError:
            i = 0
            while True:
                i += 1
                try:
                    os.rename(file, os.path.join(self.deleted,
                                                 file + "_" + str(i)))
                except OSError:
                    continue
                else:
                    break

        self.reload_dir()
        self.stdscr.clear()
        self.print_contents(file + " deleted")

    def delete_marked(self):
        if self.marked == []:
            self.print_contents("No marked elements")
        else:
            original_cwd = self.cwd
            for marked_obj in self.marked:
                marked_path = marked_obj.dir_location
                os.chdir(marked_path)
                for marked_entry in marked_obj.marked_entries:
                    self.delete_file(marked_entry)
                    # self.print_contents(marked_path + " /" + marked_entry)
                    # time.sleep(1)
            os.chdir(original_cwd)

#     def move_file(self, file, destination):
#         self.reload_dir()
#         dest_path = destination + "/" + file
#         try:
#             # os.rename(file, dest_path)
#             shutil.move(file, destination),
#         except(IsADirectoryError):
#             self.print_contents("Destination: " + dest_path
#                                 + " is a directory")
#             time.sleep(2)
#         except (FileNotFoundError):
#             self.print_contents(file + " does not exist")
#             time.sleep(2)
#         except (OSError):
#             # as error:
#             self.print_contents(file)
#             # self.print_contents(str(error) + ": can't move "
#             #                     + dest_path)
#             time.sleep(2)
#             return
#         else:
#             # self.reload_dir()
#             self.print_contents(file + " moved to " + dest_path)
#             time.sleep(2)

    def move_marked(self, destination):
        if self.marked == []:
            self.print_contents("No marked elements")
        else:
            # original_cwd = self.cwd
            for marked_obj in self.marked:
                marked_path = marked_obj.dir_location
                # os.chdir(marked_path)
                for marked_entry in marked_obj.marked_entries:
                    try:
                        shutil.move(os.path.join(marked_path, marked_entry),
                                    destination)
                    except shutil.Error:
                        self.print_contents("")
            self.reload_dir()
            self.marked = []
            self.print_contents()

    # moves cursor to  cursor + offset
    # invokes print of  contents based on new cursor postition
    def move_cursor(self, offset):
        if offset > 0:
            if (self.curr_pos + offset) <= self.max_pos:
                self.curr_pos += offset
                if ((self.curr_pos >= (self.curr_top + self.bottom_offset)
                     - self.bottom_offset//3)
                        and ((self.curr_top +
                             self.bottom_offset) <= self.max_pos)):
                    self.curr_top += offset
            else:
                self.curr_pos = self.max_pos
        if offset < 0 and (self.curr_pos + offset) >= 0:
            self.curr_pos += offset
            if self.curr_pos < self.curr_top + self.bottom_offset//3:
                self.curr_top += offset
                if self.curr_top < 0:
                    self.curr_top = 0
        self.print_contents()

    def check_pid(self, pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def open_image(self, file):
        with open(os.devnull, 'w') as devnull:
            subprocess.call(['cp', file, '/tmp/slipy/current_image'],
                            stdout=devnull, stderr=devnull)
            if self.sxiv_pid == 0 or not self.check_pid(self.sxiv_pid):
                self.print_contents(str(
                    self.check_pid(self.sxiv_pid)) + str(self.sxiv_pid))
                # self.sxiv_pid = os.popen('sxiv /tmp/slipy/current_image')
                sxiv_proc = subprocess.Popen(
                    ['sxiv', '/tmp/slipy/current_image'],
                    stdout=devnull, stderr=devnull)
                self.sxiv_pid = sxiv_proc.pid
                # self.print_stuff(self.sxiv_pid)
            else:
                self.print_contents(str(
                    self.check_pid(self.sxiv_pid)) + str(self.sxiv_pid))

    def open_with(self, file, program):
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(
                [program, file], stdout=devnull, stderr=devnull)

    def get_dir_depth(self, path):
        return path.count("/")

    def open_file(self, file):
        file_ext = os.path.splitext(self.dir_contents[self.curr_pos])[1]
        if file_ext == "":
            if os.path.isdir(file):
                self.change_dir(file)
            else:
                subprocess.Popen(['rxvt', '-e', 'vim', file])
        elif (file_ext == ".png"
                or file_ext == ".jpg"
                or file_ext == ".jpeg"):
            self.open_image(file)
        elif file_ext == ".pdf":
            self.open_with(file, 'zathura')
        elif file_ext == ".mp3":
            with open(os.devnull, 'w') as devnull:
                subprocess.Popen(
                    ["mpv", "--external-file",
                     self.music_icon,
                     "--audio-display=attachment",
                     "--keep-open=yes", file],
                    stdout=devnull, stderr=devnull)
        elif(file_ext == ".gif"):
            with open(os.devnull, 'w') as devnull:
                subprocess.Popen(
                    ["mpv",
                     "--loop-file=inf", file],
                    stdout=devnull, stderr=devnull)
        elif (file_ext == ".mp4"
                or file_ext == ".mkv"
                or file_ext == ".m4a"
                or file_ext == ".webm"):
            with open(os.devnull, 'w') as devnull:
                subprocess.Popen(
                    ["mpv", "--keep-open=yes", file],
                    stdout=devnull, stderr=devnull)

    def rename_file(self, file):
        renamefile = self.tmpfile + "renamefile"
        with open(renamefile, 'w') as rnfile:
            rnfile.write(file)
        with open(renamefile, 'r') as rnfile:
            oldname = rnfile.readlines()[0]
        curses.endwin()
        curses.savetty()
        with open(renamefile, 'r') as rnfile:
            subprocess.run(["vim", renamefile])
            curses.resetty()
            self.stdscr.refresh()
            curses.curs_set(0)
            newname = rnfile.read().splitlines()[0]
            if newname in self.dir_contents:
                self.print_contents(newname + " already exists")
            elif oldname != newname and newname != "x":
                os.rename(oldname, newname)
                self.dir_contents[self.curr_pos] = newname
                self.print_contents(newname)
