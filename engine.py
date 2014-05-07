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
        print 'Shotgun Debug: %s' % msg

    def log_info(self, msg):
        print 'Shotgun Log: %s' % msg

    def log_warning(self, msg):
        msg = 'Shotgun Warning: %s' % msg
        print msg
        mari.utils.message(msg)

    def log_error(self, msg):
        msg = 'Shotgun Error: %s' % msg
        print msg
        mari.utils.message(msg)
