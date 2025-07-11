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
import os


# Mari versions compatibility constants
VERSION_OLDEST_COMPATIBLE = (5, 0, 0)
VERSION_OLDEST_SUPPORTED = (6, 0, 3)
VERSION_NEWEST_SUPPORTED = (7, 1, 99)
# Caution: make sure compatibility_dialog_min_version default value in info.yml
# is equal to VERSION_NEWEST_SUPPORTED


class MariEngine(sgtk.platform.Engine):
    """
    The engine class
    """

    @property
    def host_info(self):
        """
        :returns: A dictionary with information about the application hosting this engine.

        The returned dictionary is of the following form on success:

            {
                "name": "Mari",
                "version": "1.2.3",
            }

        The returned dictionary is of following form on an error preventing
        the version identification.

            {
                "name": "Mari",
                "version: "unknown"
            }
        """
        host_info = {"name": "Mari", "version": "unknown"}

        try:
            mari_version = mari.app.version()

            host_info["version"] = "%s.%s.%s" % (
                mari_version.major(),
                mari_version.minor(),
                mari_version.revision(),
            )

        except:
            # Fallback to initialization value above
            pass

        return host_info

    def pre_app_init(self):
        """
        Engine construction/setup done before any apps are initialized
        """
        self.log_debug("%s: Initializing..." % self)

        # check that this version of Mari is supported:
        mari_version = (
            mari.app.version().major(),
            mari.app.version().minor(),
            mari.app.version().revision(),
        )

        url_doc_supported_versions = "https://help.autodesk.com/view/SGDEV/ENU/?guid=SGD_si_integrations_engine_supported_versions_html"

        if mari_version < VERSION_OLDEST_COMPATIBLE:
            # Older than the oldest compatible version

            # No mari.utils.message here because Mari will issue a warning
            # message from the TankError exception

            raise sgtk.TankError(
                """
Flow Production Tracking is no longer compatible with {product} versions older
than {version}.

For information regarding support engine versions, please visit this page:
{url_doc_supported_versions}
                """.strip().format(
                    product="Mari",
                    url_doc_supported_versions=url_doc_supported_versions,
                    version=self.version_str(VERSION_OLDEST_COMPATIBLE),
                )
            )

        elif mari_version < VERSION_OLDEST_SUPPORTED:
            # Older than the oldest supported version
            self.logger.warning(
                "Flow Production Tracking no longer supports {product} "
                "versions older than {version}".format(
                    product="Mari",
                    version=self.version_str(VERSION_OLDEST_SUPPORTED),
                )
            )

            if self.has_ui:
                mari.utils.message(
                    """
Flow Production Tracking no longer supports {product} versions older than
{version}.
You can continue to use Toolkit but you may experience bugs or instabilities.

For information regarding support engine versions, please visit this page:
{url_doc_supported_versions}
                    """.strip()
                    .replace(
                        # Precense of \n breaks the Rich Text Format
                        "\n",
                        "<br>",
                    )
                    .format(
                        product="Mari",
                        url_doc_supported_versions='<a style="color: {color}" href="{u}">{u}</a>'.format(
                            u=url_doc_supported_versions,
                            color=sgtk.platform.constants.SG_STYLESHEET_CONSTANTS.get(
                                "SG_HIGHLIGHT_COLOR",
                                "#18A7E3",
                            ),
                        ),
                        version=self.version_str(VERSION_OLDEST_SUPPORTED),
                    ),
                    title="Warning - Flow Production Tracking Compatibility!".ljust(
                        # Padding to try to prevent the dialog being insanely narrow
                        70
                    ),
                    icon=sgtk.platform.qt.QtGui.QMessageBox.Warning,
                )

        elif mari_version < VERSION_NEWEST_SUPPORTED:
            # Within the range of supported versions
            self.logger.debug(
                f"Running Mari version { self.version_str(mari_version) }"
            )

        else:
            # Newer than the newest supported version
            # This is an untested version of Mari.
            self.logger.warning(
                "Flow Production Tracking has not yet been fully tested with "
                "{product} version {version}.".format(
                    product="Mari",
                    version=self.version_str(mari_version),
                )
            )

            if (
                self.has_ui
                and "SGTK_MARI_VERSION_WARNING_SHOWN" not in os.environ
                and mari_version[0]
                >= self.get_setting("compatibility_dialog_min_version")
            ):
                # show the warning dialog the first time
                os.environ["SGTK_MARI_VERSION_WARNING_SHOWN"] = "1"

                mari.utils.message(
                    """
Flow Production Tracking has not yet been fully tested with {product} version
{version}.
You can continue to use Toolkit but you may experience bugs or instabilities.

Please report any issues to:
{support_url}
                    """.strip()
                    .replace(
                        # Precense of \n breaks the Rich Text Format
                        "\n",
                        "<br>",
                    )
                    .format(
                        product="Mari",
                        support_url='<a style="color: {color}" href="{u}">{u}</a>'.format(
                            u=sgtk.support_url,
                            color=sgtk.platform.constants.SG_STYLESHEET_CONSTANTS.get(
                                "SG_HIGHLIGHT_COLOR",
                                "#18A7E3",
                            ),
                        ),
                        version=self.version_str(mari_version),
                    ),
                    title="Warning - Flow Production Tracking Compatibility!".ljust(
                        # Padding to try to prevent the dialog being insanely narrow
                        70
                    ),
                    icon=sgtk.platform.qt.QtGui.QMessageBox.Warning,
                )

        # cache handles to the various manager instances:
        tk_mari = self.import_module("tk_mari")
        self.__geometry_mgr = tk_mari.GeometryManager()
        self.__project_mgr = tk_mari.ProjectManager()
        self.__metadata_mgr = tk_mari.MetadataManager()

    def post_app_init(self):
        """
        Do any initialization after apps have been loaded
        """
        if self.has_ui:
            # create the Shotgun menu
            tk_mari = self.import_module("tk_mari")
            self._menu_generator = tk_mari.MenuGenerator(self)
            self._menu_generator.create_menu()

        # Update the current Mari project with the current context so that next time this project is
        # opened, the work area changes accordingly.
        #
        # Note, currently this will happen every time as long as Shotgun is running so it will update
        # any opened projects even if they were never previously opened in Shotgun...  This just adds
        # some metadata to the project though so shouldn't be a big deal!  If it is then we should
        # make it less automatic.
        current_project = mari.projects.current()
        if current_project:
            self.log_debug(
                "Updating the Work Area on the current project to '%s'" % self.context
            )
            self.__metadata_mgr.set_project_metadata(current_project, self.context)

        # connect to Mari project events:
        mari.utils.connect(mari.projects.opened, self.__on_project_opened)

    def destroy_engine(self):
        """
        Called when the engine is being destroyed
        """
        self.log_debug("%s: Destroying..." % self)

        if self.has_ui:
            # destroy the menu:
            self._menu_generator.destroy_menu()

        # disconnect from Mari project events:
        mari.utils.disconnect(mari.projects.opened, self.__on_project_opened)

    @property
    def has_ui(self):
        """
        Detect and return if mari is not running in terminal mode
        """
        return not mari.app.inTerminalMode()

    @classmethod
    def version_str(cls, version_tuple):
        return "{}.{}v{}".format(*version_tuple)

    def find_geometry_for_publish(self, sg_publish):
        """
        Find the geometry and version info for the specified publish if it exists in the current project

        :param sg_publish:  The Shotgun publish to find geo for.  This is a Shotgun entity dictionary
                            containing at least the entity "type" and "id".
        :returns:           Tuple containing the geo and version that match the publish if found.
        """
        return self.__geometry_mgr.find_geometry_for_publish(sg_publish)

    def list_geometry(self):
        """
        Find all Shotgun aware geometry in the scene.  Any non-Shotgun aware geometry is ignored!

        :returns:   A list of dictionaries containing the geo together with any Shotgun info
                    that was found on it
        """
        return self.__geometry_mgr.list_geometry()

    def list_geometry_versions(self, geo):
        """
        Find all Shotgun aware versions for the specified geometry.  Any non-Shotgun aware versions are
        ignored!

        :param geo: The Mari GeoEntity to find all versions for
        :returns:   A list of dictionaries containing the geo_version together with any Shotgun info
                    that was found on it
        """
        return self.__geometry_mgr.list_geometry_versions(geo)

    def load_geometry(self, sg_publish, options=None, objects_to_load=None):
        """
        Wraps the Mari GeoManager.load() method and additionally tags newly loaded geometry with Shotgun
        specific metadata.  See Mari API documentation for more information on GeoManager.load().

        :param sg_publish:      The shotgun publish to load.  This should be a Shotgun entity dictionary
                                containing at least the entity "type" and "id".
        :param options:         [Mari arg] - Options to be passed to the file loader when loading the geometry
        :param objects_to_load: [Mari arg] - A list of objects to load from the file
        :returns:               A list of the loaded GeoEntity instances that were created
        """
        return self.__geometry_mgr.load_geometry(sg_publish, options, objects_to_load)

    def get_shotgun_info(self, mari_entity):
        """
        Get all Shotgun info stored with the specified mari entity.

        :param mari_entity: The mari entity to query metadata from.
        :returns:           Dictionary containing all Shotgun metadata found
                            in the Mari entity.
        """
        return self.__metadata_mgr.get_metadata(mari_entity)

    def add_geometry_version(self, geo, sg_publish, options=None):
        """
        Wraps the Mari GeoEntity.addVersion() method and additionally tags newly loaded geometry versions
        with Shotgun specific metadata. See Mari API documentation for more information on
        GeoEntity.addVersion().

        :param geo:             The Mari GeoEntity to add a version to
        :param sg_publish:      The publish to load as a new version.  This should be a Shotgun entity dictionary
                                containing at least the entity "type" and "id".
        :param options:         [Mari arg] - Options to be passed to the file loader when loading the geometry.  The
                                options will default to the options that were used to load the current version if
                                not specified.
        :returns:               The new GeoEntityVersion instance
        """
        return self.__geometry_mgr.add_geometry_version(geo, sg_publish, options)

    def create_project(
        self,
        name,
        sg_publishes,
        channels_to_create,
        channels_to_import=[],
        project_meta_options=None,
        objects_to_load=None,
    ):
        """
        Wraps the Mari ProjectManager.create() method and additionally tags newly created project and all
        loaded geometry & versions with Shotgun specific metadata. See Mari API documentation for more
        information on ProjectManager.create().

        :param name:                    [Mari arg] - The name to use for the new project
        :param sg_publishes:            A list of publishes to load into the new project.  At least one publish
                                        must be specified!  Each entry in the list should be a Shotgun entity
                                        dictionary containing at least the entity "type" and "id".
        :param channels_to_create:      [Mari arg] - A list of channels to create for geometry in the new project
        :param channels_to_import:      [Mari arg] - A list of channels to import for geometry in the new project
        :param project_meta_options:    [Mari arg] - A dictionary of project creation meta options - these are
                                        typically the mesh options used when loading the geometry
        :param objects_to_load:         [Mari arg] - A list of objects to load from the files
        :returns:                       The newly created Project instance
        """
        return self.__project_mgr.create_project(
            name,
            sg_publishes,
            channels_to_create,
            channels_to_import,
            project_meta_options,
            objects_to_load,
        )

    def log_debug(self, msg):
        """
        Log a debug message
        :param msg:    The debug message to log
        """
        if not hasattr(self, "_debug_logging"):
            self._debug_logging = self.get_setting("debug_logging", False)
        if self._debug_logging:
            print("PTR Debug: %s" % msg)

    def log_info(self, msg):
        """
        Log some info
        :param msg:    The info message to log
        """
        print("SG Info: %s" % msg)

    def log_warning(self, msg):
        """
        Log a warning
        :param msg:    The warning message to log
        """
        msg = "PTR Warning: %s" % msg
        print(msg)
        # mari.utils.message(msg)

    def log_error(self, msg):
        """
        Log an error
        :param msg:    The error message to log
        """
        msg = "PTR Error: %s" % msg
        print(msg)
        mari.utils.message(msg)

    def __on_project_opened(self, opened_project, is_new):
        """
        Called when a project is opened in Mari.  This looks for Toolkit metadata on the newly opened
        project and if it finds any, it tries to build a new context and restarts the engine with this
        new context.

        :param opened_project:  The mari Project instance for the newly opened project
        :param is_new:          True if the opened project is a new project
        """
        if is_new:
            # for now, do nothing with new projects.
            # TODO: should we tag project with metadata?
            return

        self.log_debug(
            "Project opened - attempting to set the current Work Area to match..."
        )

        # get the context for the project that's been opened
        # using the metadata stored on the project (if available):
        md = self.__metadata_mgr.get_project_metadata(opened_project)
        if not md:
            # This project has never been opened with Toolkit running before
            # so don't need to do anything!
            self.log_debug("Work area unchanged - the opened project is not PTR aware!")
            return

        # try to determine the project context from the metadata:
        ctx_entity = None
        if md.get("task_id"):
            ctx_entity = {"type": "Task", "id": md["task_id"]}
        elif md.get("entity_id") and md.get("entity_type"):
            ctx_entity = {"type": md["entity_type"], "id": md["entity_id"]}
        elif md.get("project_id"):
            ctx_entity = {"type": "Project", "id": md["project_id"]}
        else:
            # failed to determine the context for the project!
            self.log_debug(
                "Work area unchanged - failed to determine a context for the opened project!"
            )
            return

        # get the context from the context entity:
        ctx = None
        try:
            ctx = self.sgtk.context_from_entity(ctx_entity["type"], ctx_entity["id"])
        except sgtk.TankError as e:
            self.log_error(
                "Work area unchanged - Failed to create context from '%s %s': %s"
                % (ctx_entity["type"], ctx_entity["id"], e)
            )
            return

        if ctx == self.context:
            # nothing to do - context is the same!
            return

        # The context for project is different so restart engine
        # with this context:
        try:
            self.log_debug("Restarting the engine for Work Area: %s" % ctx)

            # stop current engine:
            self.destroy()

            # start new engine with the new context:
            sgtk.platform.start_engine(self.name, ctx.sgtk, ctx)
        except sgtk.TankError as e:
            self.log_error("Failed to start PTR engine for Work Area %s: %s" % (ctx, e))
        except Exception as e:
            self.log_exception("Failed to start PTR engine for Work Area %s" % ctx)
