import mari

class MenuGenerator(object):
    def __init__(self, engine):
        self._engine = engine

    def create_menu(self):
        shotgun_menu = 'MainWindow/Shotgun'

        # now enumerate all items and create menu objects for them
        menu_items = []
        for (cmd_name, cmd_details) in self._engine.commands.items():
            menu_items.append( AppCommand(cmd_name, cmd_details) )

        for cmd in menu_items:
            cmd.add_command_to_menu(shotgun_menu)

    def destroy_menu(self):
        mari._menu_commands = {}


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
