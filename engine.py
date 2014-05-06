import mari.utils

import tank

class MariEngine(tank.platform.Engine):
    
    def init_engine(self):
        self.log_debug("%s: Initializing..." % self)
    
    def post_app_init(self):
        # create menus
        tk_mari = self.import_module("tk_mari")
        self._menu_generator = tk_mari.MenuGenerator(self)
        self._menu_generator.create_menu()

    def destroy_engine(self):
        self.log_debug("%s: Destroying..." % self)
        self._menu_generator.destroy_menu()

    def log_debug(self, msg):
        pass

    def log_info(self, msg):
        pass

    def log_warning(self, msg):
        pass

    def log_error(self, msg):
        pass
