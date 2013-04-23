import tank
import hiero.core


class HieroEngine(tank.platform.Engine):
    def init_engine(self):
        """
        """
        # # Copied from Nuke Engine
        self.log_debug("%s: Initializing..." % self)

        if self.context.project is None:
            # must have at least a project in the context to even start!
            raise tank.TankError("The Tank engine needs at least a project in the context "
                                 "in order to start! Your context: %s" % self.context)

    def post_app_init(self):
        """
        Called when all apps have initialized
        """
        # create menus
        tk_hiero = self.import_module("tk_hiero")
        self._menu_generator = tk_hiero.MenuGenerator(self)
        self._menu_generator.create_menu()

    def destroy_engine(self):
        """
        """
        self.log_debug("%s: Destroying..." % self)
        self._menu_generator.destroy_menu()

    def log_debug(self, msg):
        """
        """
        if self.get_setting("debug_logging", False):
            # print it in the console
            msg = "Tank Debug: %s" % msg
            print msg

    def log_info(self, msg):
        """
        """
        msg = "Tank Info: %s" % msg
        print msg

    def log_warning(self, msg):
        """
        """
        msg = "Tank Warning: %s" % msg
        print msg

    def log_error(self, msg):
        """
        """
        msg = "Tank Error: %s" % msg
        print msg
