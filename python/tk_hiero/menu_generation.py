# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys
import os
import hiero
import unicodedata

from PySide import QtGui

class MenuGenerator(object):
    def __init__(self, engine):
        self._engine = engine
        self._menu_handle = None
        self._context_menus_to_apps = None

    def create_menu(self):
        """
        Create the Tank Menu
        """
        if self._menu_handle is not None:
            self.destroy_menu()

        self._menu_handle = QtGui.QMenu("Shotgun")
        help = hiero.ui.findMenuAction("Cache")
        menuBar = hiero.ui.menuBar()
        menuBar.insertMenu(help, self._menu_handle)

        self._menu_handle.clear()

        # now add the context item on top of the main menu
        self._context_menu = self._add_context_menu()
        self._menu_handle.addSeparator()

        # now enumerate all items and create menu objects for them
        menu_items = []
        for (cmd_name, cmd_details) in self._engine.commands.items():
            menu_items.append(AppCommand(self._engine, cmd_name, cmd_details))

        # now add favourites
        for fav in self._engine.get_setting("menu_favourites"):
            app_instance_name = fav["app_instance"]
            menu_name = fav["name"]
            # scan through all menu items
            for cmd in menu_items:
                if cmd.get_app_instance_name() == app_instance_name and cmd.name == menu_name:
                    # found our match!
                    cmd.add_command_to_menu(self._menu_handle)
                    # mark as a favourite item
                    cmd.favourite = True

        # get the apps for the various context menus
        self._context_menus_to_apps = {
            "bin_context_menu": [],
            "timeline_context_menu": [],
            "spreadsheet_context_menu": [],
        }

        remove = set()
        for (key, apps) in self._context_menus_to_apps.iteritems():
            items = self._engine.get_setting(key)
            for item in items:
                app_instance_name = item["app_instance"]
                menu_name = item["name"]
                # scan through all menu items
                for (i, cmd) in enumerate(menu_items):
                    if cmd.get_app_instance_name() == app_instance_name and cmd.name == menu_name:
                        # found th match
                        apps.append(cmd)
                        cmd.requires_selection = item["requires_selection"]
                        if not item["keep_in_menu"]:
                            remove.add(i)
                        break

        for index in sorted(remove, reverse=True):
            del menu_items[index]

        # register for the interesting events
        hiero.core.events.registerInterest("kShowContextMenu/kBin", self.eventHandler)
        hiero.core.events.registerInterest("kShowContextMenu/kTimeline", self.eventHandler)
        # note that the kViewer works differently than the other things
        # (returns a hiero.ui.Viewer object: http://docs.thefoundry.co.uk/hiero/10/hieropythondevguide/api/api_ui.html#hiero.ui.Viewer)
        # so we cannot support this easily using the same principles as for the other things....
        #hiero.core.events.registerInterest('kShowContextMenu/kViewer', self.eventHandler)
        hiero.core.events.registerInterest("kShowContextMenu/kSpreadsheet", self.eventHandler)

        self._menu_handle.addSeparator()

        # now go through all of the menu items.
        # separate them out into various sections
        commands_by_app = {}

        for cmd in menu_items:
            if cmd.get_type() == "context_menu":
                # context menu!
                cmd.add_command_to_menu(self._context_menu)
            else:
                # normal menu
                app_name = cmd.get_app_name()
                if app_name is None:
                    # un-parented app
                    app_name = "Other Items"
                if not app_name in commands_by_app:
                    commands_by_app[app_name] = []
                commands_by_app[app_name].append(cmd)

        # now add all apps to main menu
        self._add_app_menu(commands_by_app)

    def destroy_menu(self):
        menuBar = hiero.ui.menuBar()
        menuBar.removeAction(self._menu_handle.menuAction())
        self._menu_handle = None

    def eventHandler(self, event):
        if event.subtype == "kBin":
            cmds = self._context_menus_to_apps["bin_context_menu"]
        elif event.subtype == "kTimeline":
            cmds = self._context_menus_to_apps["timeline_context_menu"]
        elif event.subtype == "kSpreadsheet":
            cmds = self._context_menus_to_apps["spreadsheet_context_menu"]

        if not cmds:
            return

        event.menu.addSeparator()
        menu = event.menu.addAction("Shotgun")
        menu.setEnabled(False)

        for cmd in cmds:
            enabled = True
            if cmd.requires_selection:
                if hasattr(event.sender, "selection") and not event.sender.selection():
                    enabled = False
            cmd.sender = event.sender
            cmd.eventType = event.type
            cmd.eventSubtype = event.subtype
            cmd.add_command_to_menu(event.menu, enabled)
        event.menu.addSeparator()

    def _add_context_menu(self):
        """
        Adds a context menu which displays the current context
        """
        ctx = self._engine.context

        if ctx.entity is None:
            ctx_name = "%s" % ctx.project["name"]
        elif ctx.step is None and ctx.task is None:
            # entity only
            # e.g. Shot ABC_123
            ctx_name = "%s %s" % (ctx.entity["type"], ctx.entity["name"])
        else:
            # we have either step or task
            task_step = None
            if ctx.step:
                task_step = ctx.step.get("name")
            if ctx.task:
                task_step = ctx.task.get("name")

            # e.g. [Lighting, Shot ABC_123]
            ctx_name = "%s, %s %s" % (task_step, ctx.entity["type"], ctx.entity["name"])

        # create the menu object
        ctx_menu = self._menu_handle.addMenu(ctx_name)
        action = ctx_menu.addAction("Jump to Shotgun")
        action.triggered.connect(self._jump_to_sg)
        action = ctx_menu.addAction("Jump to File System")
        action.triggered.connect(self._jump_to_fs)
        ctx_menu.addSeparator()

        return ctx_menu

    def _jump_to_sg(self):
        """
        Jump from context to Sg
        """
        from tank.platform.qt import QtCore, QtGui
        url = self._engine.context.shotgun_url
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _jump_to_fs(self):
        """
        Jump from context to Fs
        """
        paths = self._engine.context.filesystem_locations
        for disk_location in paths:
            # get the setting
            system = sys.platform

            # run the app
            if system == "linux2":
                cmd = 'xdg-open "%s"' % disk_location
            elif system == "darwin":
                cmd = 'open "%s"' % disk_location
            elif system == "win32":
                cmd = 'cmd.exe /C start "Folder" "%s"' % disk_location
            else:
                raise Exception("Platform '%s' is not supported." % system)

            exit_code = os.system(cmd)
            if exit_code != 0:
                self._engine.log_error("Failed to launch '%s'!" % cmd)

    def _add_app_menu(self, commands_by_app):
        """
        Add all apps to the main menu, process them one by one.
        """
        for app_name in sorted(commands_by_app.keys()):
            if len(commands_by_app[app_name]) > 1:
                # more than one menu entry fort his app
                # make a sub menu and put all items in the sub menu
                app_menu = self._menu_handle.addMenu(app_name)
                for cmd in commands_by_app[app_name]:
                    cmd.add_command_to_menu(app_menu)
            else:
                # this app only has a single entry.
                # display that on the menu
                # todo: Should this be labeled with the name of the app
                # or the name of the menu item? Not sure.
                cmd_obj = commands_by_app[app_name][0]
                if not cmd_obj.favourite:
                    # skip favourites since they are already on the menu
                    cmd_obj.add_command_to_menu(self._menu_handle)


class AppCommand(object):
    """
    Wraps around a single command that you get from engine.commands
    """
    def __init__(self, engine, name, command_dict):
        self.name = name
        self.engine = engine
        self.properties = command_dict["properties"]
        self.callback = command_dict["callback"]
        self.favourite = False
        self.requires_selection = False
        self.sender = None
        self.eventType = None
        self.eventSubtype = None

    def get_app_name(self):
        """
        Returns the name of the app that this command belongs to
        """
        if "app" in self.properties:
            return self.properties["app"].display_name
        return None

    def get_app_instance_name(self):
        """
        Returns the name of the app instance, as defined in the environment.
        Returns None if not found.
        """
        if "app" not in self.properties:
            return None

        app_instance = self.properties["app"]
        engine = app_instance.engine

        for (app_instance_name, app_instance_obj) in engine.apps.items():
            if app_instance_obj == app_instance:
                # found our app!
                return app_instance_name

        return None

    def get_documentation_url_str(self):
        """
        Returns the documentation as a str
        """
        if "app" in self.properties:
            app = self.properties["app"]
            doc_url = app.documentation_url
            # deal with nuke's inability to handle unicode. #fail
            if doc_url.__class__ == unicode:
                doc_url = unicodedata.normalize("NFKD", doc_url).encode("ascii", "ignore")
            return doc_url

        return None

    def get_type(self):
        """
        returns the command type. Returns node, custom_pane or default
        """
        return self.properties.get("type", "default")

    def add_command_to_menu(self, menu, enabled=True):
        """
        Adds an app command to the menu
        """
        icon = self.properties.get("icon")
        action = menu.addAction(self.name)
        action.setEnabled(enabled)
        if icon:
            action.setIcon(QtGui.QIcon(icon))

        def handler():
            # populate special action context
            # this is read by apps and hooks 
            
            # in hiero, sender parameter for hiero.core.events.EventType.kShowContextMenu
            # is supposed to always of class binview:
            #
            # http://docs.thefoundry.co.uk/hiero/10/hieropythondevguide/api/api_ui.html?highlight=sender#hiero.ui.BinView
            #
            # In reality, however, it seems it returns the following items:
            # ui.Hiero.Python.TimelineEditor object at 0x11ab15248
            # ui.Hiero.Python.SpreadsheetView object at 0x11ab152d8>
            # ui.Hiero.Python.BinView
            #
            # These objects all have a selection property that returns a list of objects.
            # We extract the selected objects and set the engine "last clicked" state:
            
            # set the engine last clicked selection state
            if self.sender:
                self.engine._last_clicked_selection = self.sender.selection()
            else:
                # main menu
                self.engine._last_clicked_selection = []
            
            # set the engine last clicked selection area
            if self.eventType == "kBin":
                self.engine._last_clicked_area = self.engine.HIERO_BIN_AREA
            
            elif self.eventType == "kTimeline":
                self.engine._last_clicked_area = self.engine.HIERO_TIMELINE_AREA
            
            elif self.eventType == "kSpreadsheet":
                self.engine._last_clicked_area = self.engine.HIERO_SPREADSHEET_AREA
            
            else:
                self.engine._last_clicked_area = None
            
            self.engine.log_debug("")
            self.engine.log_debug("--------------------------------------------")
            self.engine.log_debug("A menu item was clicked!")
            self.engine.log_debug("Event Type: %s / %s" % (self.eventType, self.eventSubtype))
            self.engine.log_debug("Selected Objects:")
            for x in self.engine._last_clicked_selection:
                self.engine.log_debug("- %r" % x)
            self.engine.log_debug("--------------------------------------------")
            
            # and fire the callback
            self.callback()


        action.triggered.connect(handler)
