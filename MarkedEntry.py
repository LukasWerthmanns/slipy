#!/usr/bin/python3


class MarkedDirContents:
    def __init__(self, dir_location):
        self.dir_location = dir_location
        self.marked_entries = []

    def toggle_element(self, name):
        if self.id_of_element(name) < 0:
            self.marked_entries.append(name)
        else:
            self.marked_entries.remove(name)

    def add_element(self, name):
        if self.id_of_element(name) < 0:
            self.marked_entries.append(name)

    def remove_element(self, name):
        if self.id_of_element(name) >= 0:
            self.marked_entries.remove(name)

    # returns index of name or -1 otherwise
    def id_of_element(self, name):
        try:
            return self.marked_entries.index(name)
        except ValueError:
            return -1
