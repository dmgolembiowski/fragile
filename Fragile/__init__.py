# encoding: utf-8
"""
Fragile: Terminal application for managing and tracking projects in production.
"""
#
#-----------------------------------------------------------------------------
#  Copyright (c) 2019, David Golembiowski <dmgolembiowski@gmail.com>
#
#  Distributed under the terms of the Apache License 2.0
#
#  The full license is in the file LICENSE of this repository.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports 
#-----------------------------------------------------------------------------
import threading
import time
import sys
from pathlib import Path
import datetime
import os
import socket
from .Cursedmenu import CursesMenu, SelectionMenu, curses_menu
from .Cursedmenu.items import SubmenuItem, CommandItem, MenuItem, FunctionItem
import curses
from .core import CreateProject, Main
import functools
#import pudb
#pu.db

#-----------------------------------------------------------------------------

class User:
    try:
        name = os.environ['HOME'].strip('/home/')
    except Exception:
        name = 'user'
    try:
        hname = socket.gethostname()
    except Exception:
        hname = 'fragile $ '
    termtag = name + '@' + hname


class Handler:
    def __init__(self, menu, app, cp, clas):
        """
        Handler.menu -> instance of Cursedmenu.CursesMenu
        Handler.app  -> instance of Fragile.Application
        Handler.cp   -> instance of core.CreateProject
        """
        
        self.menu = menu
        self.app = app
        self.cp = cp
        self.clas = clas

    def menu_start(self):
        self.menu.start()

    def menu_exit(self):
        self.menu.exit()

    def menu_join(self):
        self.menu.join()

    def menu_draw(self):
        self.menu.draw()

    def menu_pause(self):
        self.menu.pause()

    def menu_resume(self):
        self.menu.resume()

    def await_start(self, timeout=1):
        self.menu.wait_for_start(timeout)

    def clear_screen(self):
        self.menu.clear_screen()

    def wrap_start(self):
        self.menu.should_exit = True
        for t in threading.enumerate():
            if t is self.menu._main_thread:
                continue
            t.join()
        """
        #self.menu._main_thread.join()
        ## but currently_active_menu probably == None
        CursesMenu.currently_active_menu = None
        # ah, great, we'll just enforce it
        self.menu.should_exit = False
        try:
            self.menu.remove_exit()
        except Exception:
            pass
        try:
            self.menu._main_thread = threading.Thread(
                    target=self.menu._wrap_start,
                    daemon=True)
        except TypeError:
            self.menu._main_thread = threading.Thread(
                    target=self._wrap_start)
            self.menu._main_thread.daemon = True
        self.menu._main.daemon = True
        self.menu._main_thread.start()
        self.menu._main_thread.join(timeout=None)
        if self.menu.parent is None:
            curses.wrapper(self.menu._main_loop)
        else:
            self.menu._main_loop(None)
        CursesMenu.currently_active_menu = None
        self.menu.clear_screen()
        curses_menu.clear_terminal()
        CursesMenu.currently_active_menu = self.menu.previous_active_menu
        """
        self.menu.clear_screen()
        curses_menu.clear_terminal()

class FragileProject(FunctionItem):
    each = []
    def __init__(self, name, datastructure, function=lambda: None, args=[]):
        self.name = name
        self.datastructure = datastructure
        self.function = function
        self.args = args
        FragileProject.each.append(self)

    def __str__(self):
        return self.name

    @staticmethod
    def refresh_saved(f):
        FragileProject.each = []
        return f

class Application:
    def __init__(self):
        pass

    def start_fragile(self):
        curses_menu.clear_terminal()
        descr = 'A local goal-planning kanban board inspired by Agile methodologies.'
        menu = CursesMenu('Fragile Project Manager', descr, show_exit_option=False)
        handler = Handler(menu=menu, app=self, cp=CreateProject, clas=Application)

        @FragileProject.refresh_saved
        def launch():
            nonlocal descr
            nonlocal menu
            nonlocal handler
            PATH_TO_FRAGILE = str(Path(__file__).parent.absolute())
            PATH_TO_RECORDS = PATH_TO_FRAGILE + '/records.pydict'

            # Get all of the saved projects
            with open(PATH_TO_RECORDS, 'r') as recs:
                _records = recs.read()
            records = eval(_records)    
            projects = records['all']

            # Iterate over each of the projects and make a FragileProject instance
            for project in projects:
                FragileProject(projects[project]['projectName'], projects[project])
            
            options = SelectionMenu(FragileProject.each)

            __openProject__ = SubmenuItem("Open a saved Fragile Project", options)

            __createNew__ = FunctionItem(
                    "Create a new Fragile Project",
                    Main.main,
                    args=[handler])


            __memberSpace__ = FunctionItem(
                    "Open a Team Member's Fragile Board",
                    lambda: None,
                    args=[handler])


            __lookup__ = MenuItem(
                    "Search projects for a file")


            __admin__  = MenuItem(
                    "Team Administration")


            __dock__   = MenuItem(
                    "Configure External Connections")


            __dash__   = MenuItem(
                    "Dashboard Overview of a Fragile Project")


            __cal__    = MenuItem(
                    "Calendar of Upcoming Deadlines")


            __export__ = MenuItem(
                    "Export all project records")


            __services__ = MenuItem(
                    "Manage background Fragile jobs, platforms, services, etc.")


            __exit__ = FunctionItem(
                    "Exit",
                    sys.exit)

            for item in [
                    __openProject__,
                    __createNew__,
                    __memberSpace__,
                    __lookup__,
                    __admin__,
                    __dock__,
                    __dash__,
                    __cal__,
                    __export__,
                    __services__,
                    __exit__]:
                #cp.menu.append_item(item)
                menu.append_item(item)

            #cp.menu.show()
            menu.show()
        launch()

    @staticmethod
    def _start_fragile():
        # A sleazy way to reconnect with the main menu and redraw
        _app = Application()
        sys.exit(_app.start_fragile())

