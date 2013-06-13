"""
Copyright (c) 2013 Shotgun Software, Inc
----------------------------------------------------
"""
import hiero.core

import tank


class HieroEngine(tank.platform.Engine):
    def init_engine(self):
        if self.get_setting("debug_logging", False):
            hiero.core.log.setLogLevel(hiero.core.log.kDebug)

        self.log_debug("%s: Initializing..." % self)

        if self.context.project is None:
            # must have at least a project in the context to even start!
            raise tank.TankError("The Tank engine needs at least a project in the context "
                                 "in order to start! Your context: %s" % self.context)

    def post_app_init(self):
        # create menus
        tk_hiero = self.import_module("tk_hiero")
        self._menu_generator = tk_hiero.MenuGenerator(self)
        self._menu_generator.create_menu()

    def destroy_engine(self):
        self.log_debug("%s: Destroying..." % self)
        self._menu_generator.destroy_menu()

    # Logging
    ############################################################################
    def log_debug(self, msg, *args):
        hiero.core.log.debug(msg, *args)

    def log_info(self, msg, *args):
        hiero.core.log.info(msg, *args)

    def log_warning(self, msg, *args):
        hiero.core.log.info("Warning: %s" % msg, *args)

    def log_error(self, msg, *args):
        hiero.core.log.error(msg, *args)
