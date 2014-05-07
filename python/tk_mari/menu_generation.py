import os
import sys
import mari
from tank.platform.qt import QtGui, QtCore

class MenuGenerator(object):
    def __init__(self, engine):
        self._engine = engine

    def create_menu(self):
        shotgun_menu = 'MainWindow/Shotgun'

        context_menu = self._add_context_menu(shotgun_menu)

        # now enumerate all items and create menu objects for them
        menu_items = []
        for (cmd_name, cmd_details) in self._engine.commands.items():
            menu_items.append(AppCommand(cmd_name, cmd_details))

        for cmd in menu_items:
            if cmd.get_type() == 'context_menu':
                cmd.add_command_to_menu(context_menu)
            else:
                cmd.add_command_to_menu(shotgun_menu)


    def destroy_menu(self):
        mari._menu_commands = {}
        shotgun_menu = 'Shotgun'

        ctx = self._engine.context
        ctx_name = str(ctx)
        ctx_menu = '%s/%s' % (shotgun_menu, ctx_name)

        context_actions = mari.menus.actions('MainWindow', '%s' % shotgun_menu, '%s' % ctx_name)
        for action in context_actions:
            mari.menus.removeAction('MainWindow/%s/%s' % (ctx_menu, action.name()))

        shotgun_actions = mari.menus.actions('MainWindow', shotgun_menu)
        for action in shotgun_actions:
            mari.menus.removeAction('MainWindow/%s/%s' % (shotgun_menu, action.name()))


    def _add_context_menu(self, menu):
        mari._menu_commands = {}
        ctx = self._engine.context
        ctx_name = str(ctx)

        command_name = 'Jump To File System'
        mari._menu_commands[command_name] = self._jump_to_fs
        callback_string = 'mari._menu_commands["%s"]()' % command_name

        action = mari.actions.create(command_name, callback_string)
        mari.menus.addAction(action, '%s/%s' % (menu, ctx_name))

        command_name = 'Jump To Shotgun'
        mari._menu_commands[command_name] = self._jump_to_sg
        callback_string = 'mari._menu_commands["%s"]()' % command_name

        action = mari.actions.create(command_name, callback_string)
        mari.menus.addAction(action, '%s/%s' % (menu, ctx_name))

        return "%s/%s" % (menu, ctx_name)

    def _jump_to_sg(self):
        """
        Jump to shotgun, launch web browser
        """
        url = self._engine.context.shotgun_url
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def _jump_to_fs(self):

        """
        Jump from context to FS
        """
        # launch one window for each location on disk
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


class AppCommand(object):
    def __init__(self, name, command_dict):
        self.name = name
        self.properties = command_dict["properties"]
        self.callback = command_dict["callback"]
        self.favourite = False

    def get_app_name(self):
        if "app" in self.properties:
            return self.properties["app"].display_name
        return None

    def get_app_instance_name(self):
        if "app" not in self.properties:
            return None

        app_instance = self.properties["app"]
        engine = app_instance.engine

        for (app_instance_name, app_instance_obj) in engine.apps.items():
            if app_instance_obj == app_instance:
                # found our app!
                return app_instance_name

        return None

    def get_type(self):
        return self.properties.get("type", "default")

    def add_command_to_menu(self, menu):

        if not hasattr(mari, '_menu_commands'):
            mari._menu_commands = {}

        mari._menu_commands[self.name] = self.callback
        callback_string = 'mari._menu_commands["%s"]()' % self.name

        action = mari.actions.create(self.name, callback_string)
        mari.menus.addAction(action, menu)
