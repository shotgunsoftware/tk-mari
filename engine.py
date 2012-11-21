import tank
import hiero.core

class HieroEngine(tank.platform.Engine):

    def init_engine(self):
        """
        """
        # # Copied from Nuke Engine
        self.log_debug("%s: Initializing..." % self)

        # now check that there is a location on disk which corresponds to the context
        if self.context.entity:
            # context has an entity
            locations = self.tank.paths_from_entity(self.context.entity["type"],
                                                    self.context.entity["id"])
        elif self.context.project:
            # context has a project
            locations = self.tank.paths_from_entity(self.context.project["type"],
                                                    self.context.project["id"])
        else:
            # must have at least a project in the context to even start!
            raise tank.TankError("The hiero engine needs at least a project in the context "
                                 "in order to start! Your context: %s" % self.context)
        
        # make sure there are folders on disk
        if len(locations) == 0:
            raise tank.TankError("No folders on disk are associated with the current context. The Hiero "
                            "engine requires a context which exists on disk in order to run "
                            "correctly.")

        # create queue
        self._queue = []
        self._queue_runing = False

        # # End of copied from Nuke Engine

    def post_app_init(self):
        """
        Called when all apps have initialized
        """
        # create menus
        tk_hiero = self.import_module("tk_hiero")
        self._menu_generator = tk_hiero.MenuGenerator(self)
        self._menu_generator.create_menu()
        
        for app in self.apps.values():
            self.log_debug("%s" % app.name)

    def destroy_engine(self):
        """
        """
        self.log_debug("%s: Destroying..." % self)

    
    def log_debug(self, msg):
        """
        """
        msg = "Tank Debug: %s" % msg
        hiero.core.debug(msg)

    def log_info(self, msg):
        """
        """
        msg = "Tank Info: %s" % msg
        hiero.core.info(msg)

    def log_warning(self, msg):
        """
        """
        msg = "Tank Warning: %s" % msg
        # hiero.core.

    def log_error(self, msg):
        """
        """
        msg = "Tank Error: %s" % msg
        hiero.core.error(msg)
    
    def add_to_queue(self, name, method, args):
        """
        """
        qi = {}
        qi['name'] = name
        qi['method'] = method
        qi['args'] = args
        self._queue.append(qi)

    def report_progress(self, percent):
        """
        """

    def execute_queue(self):
        """
        """

