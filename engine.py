# Copyright (c) 2014 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
A Toolkit engine for Mari
"""

import mari
import mari.utils
import sgtk

class MariEngine(sgtk.platform.Engine):
    """
    The engine class
    """
    def init_engine(self):
        """
        Engine construction/setup
        """
        self.log_debug("%s: Initializing..." % self)
        
        tk_mari = self.import_module("tk_mari")
        self.util = tk_mari.util
    
    @property
    def has_ui(self):
        """
        Detect and return if mari is running in terminal mode
        """        
        return not mari.app.inTerminalMode()
    
    def post_app_init(self):
        """
        Do any initialization after apps have been loaded
        """
        if self.has_ui:
            # create the Shotgun menu
            tk_mari = self.import_module("tk_mari")
            self._menu_generator = tk_mari.MenuGenerator(self)
            self._menu_generator.create_menu()
            
        # connect to Mari project events:
        mari.utils.connect(mari.projects.opened, self._on_project_opened)

    def destroy_engine(self):
        """
        Called when the engine is being destroyed
        """
        self.log_debug("%s: Destroying..." % self)
        
        if self.has_ui:
            # destroy the menu:
            self._menu_generator.destroy_menu()

        # disconnect from Mari project events:
        mari.utils.disconnect(mari.projects.opened, self._on_project_opened)

    def _on_project_opened(self, opened_project, is_new):
        """
        """
        # get the context for the open project:        
        ctx = self.context_from_project(opened_project)
        if not ctx or ctx == self.context:
            # don't change anything!
            return
        
        # The context for project is different so restart engine
        # with this context:        
        try:
            # stop current engine:            
            self.destroy()
                
            # start new engine with the new context:
            sgtk.platform.start_engine(self.name, ctx.sgtk, ctx)
        except Exception, e:
            pass
        
    def context_from_project(self, mari_project):
        """
        """
        # get metadata from project:
        md = self.util.get_project_metadata(mari_project)
        if not md:
            # this project has never been opened with Toolkit running before!
            return
        
        # try to determine the project context from the metadata:
        ctx_entity = None
        if md.get("task_id"):
            ctx_entity = {"type":"Task", "id":md["task_id"]}
        elif md.get("entity_id") and md.get("entity_type"):
            ctx_entity = {"type":md["entity_type"], "id":md["entity_id"]}
        elif md.get("project_id"):
            ctx_entity = {"type":md["entity_type"], "id":md["entity_id"]}
        else:
            # failed to determine the context for the project!
            return
        
        # get the context from the context entity:
        ctx = None
        try:
            ctx = self.sgtk.context_from_entity(ctx_entity["type"], ctx_entity["id"])
        except Exception, e:
            # something went wrong when trying to build the context!
            return
        
        return ctx

    def log_debug(self, msg):
        """
        Log a debug message
        :param msg:    The debug message to log
        """
        if not hasattr(self, "_debug_logging"):
            self._debug_logging = self.get_setting("debug_logging", False)
        if self._debug_logging:
            print 'Shotgun Debug: %s' % msg

    def log_info(self, msg):
        """
        Log some info
        :param msg:    The info message to log
        """
        print 'Shotgun Log: %s' % msg

    def log_warning(self, msg):
        """
        Log a warning
        :param msg:    The warning message to log
        """        
        msg = 'Shotgun Warning: %s' % msg
        print msg
        mari.utils.message(msg)

    def log_error(self, msg):
        """
        Log an error
        :param msg:    The error message to log
        """        
        msg = 'Shotgun Error: %s' % msg
        print msg
        mari.utils.message(msg)




