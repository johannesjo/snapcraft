# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016-2017 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from snapcraft import formatting_utils


class SnapcraftError(Exception):
    """Base class for all snapcraft exceptions.

    :cvar fmt: A format string that daughter classes override

    """
    fmt = 'Daughter classes should redefine this'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.fmt.format([], **self.__dict__)

    def get_exit_code(self):
        """Exit code to use if this exception causes Snapcraft to exit."""
        return 2


class MissingStateCleanError(SnapcraftError):
    fmt = (
        "Failed to clean: "
        "Missing state for {step!r}. "
        "To clean the project, run `snapcraft clean`."
    )

    def __init__(self, step):
        super().__init__(step=step)


class StepOutdatedError(SnapcraftError):

    fmt = (
        'Failed to reuse files from previous build: '
        'The {step!r} step of {part!r} is out of date:\n'
        '{report}'
        'To clean that part\'s {step!r} step, run '
        '`snapcraft clean {parts_names} -s {step}`.'
    )

    def __init__(self, *, step, part,
                 dirty_properties=None, dirty_project_options=None,
                 dependents=None):
        messages = []
        if dirty_properties:
            humanized_properties = formatting_utils.humanize_list(
                dirty_properties, 'and')
            pluralized_connection = formatting_utils.pluralize(
                dirty_properties, 'property appears',
                'properties appear')
            messages.append(
                'The {} part {} to have changed.\n'.format(
                    humanized_properties, pluralized_connection))
        if dirty_project_options:
            humanized_options = formatting_utils.humanize_list(
                dirty_project_options, 'and')
            pluralized_connection = formatting_utils.pluralize(
                dirty_project_options, 'option appears',
                'options appear')
            messages.append(
                'The {} project {} to have changed.\n'.format(
                    humanized_options, pluralized_connection))
        if dependents:
            humanized_dependents = formatting_utils.humanize_list(
                dependents, 'and')
            pluralized_dependents = formatting_utils.pluralize(
                dependents, "depends", "depend")
            messages.append('The {0!r} step for {1!r} needs to be run again, '
                            'but {2} {3} on it.\n'.format(
                                step,
                                part,
                                humanized_dependents,
                                pluralized_dependents))
            parts_names = ['{!s}'.format(d) for d in sorted(dependents)]
        else:
            parts_names = [part]
        super().__init__(step=step, part=part,
                         report=''.join(messages),
                         parts_names=' '.join(parts_names))


class SnapcraftEnvironmentError(SnapcraftError):
    # FIXME This exception is too generic.
    # https://bugs.launchpad.net/snapcraft/+bug/1734231
    # --elopio - 20171123

    fmt = '{message}'

    def __init__(self, message):
        super().__init__(message=message)


class ContainerError(SnapcraftError):
    fmt = '{message}'

    def __init__(self, message):
        super().__init__(message=message)


class ContainerConnectionError(ContainerError):
    # FIXME this exception is too generic.
    # https://bugs.launchpad.net/snapcraft/+bug/1734233
    # --elopio - 20171123

    fmt = ('{message}\n'
           'Refer to the documentation at '
           'https://linuxcontainers.org/lxd/getting-started-cli.')


class ContainerRunError(SnapcraftError):

    fmt = (
        'The following command failed to run: '
        '{command!r} exited with {exit_code}\n'
    )

    def __init__(self, *, command, exit_code):
        if isinstance(command, list):
            command = ' '.join(command)
        super().__init__(command=command, exit_code=exit_code)


class ContainerSnapcraftCmdError(ContainerRunError):

    fmt = (
        'Snapcraft command failed in the container: '
        '{command!r} exited with {exit_code}\n'
    )

    def __init__(self, *, command, exit_code):
        if isinstance(command, list):
            command = ' '.join(command)
        super().__init__(command=command, exit_code=exit_code)


class SnapdError(SnapcraftError):
    # FIXME this exception is too generic.
    # https://bugs.launchpad.net/snapcraft/+bug/1734235
    # --elopio - 20171123

    fmt = '{message}'

    def __init__(self, message):
        super().__init__(message=message)


class PrimeFileConflictError(SnapcraftError):

    fmt = (
        'Failed to filter files: '
        'The following files have been excluded by the `stage` keyword, '
        'but included by the `prime` keyword: {fileset!r}. '
        'Edit the `snapcraft.yaml` to make sure that the files included in '
        '`prime` are also included in `stage`.'
    )


class InvalidAppCommandError(SnapcraftError):

    fmt = (
        'Failed to generate snap metadata: '
        'The specified command {command!r} defined in the app {app!r} does '
        'not exist or is not executable'
        # FIXME split the errors to include in the message how to fix them.
        # https://bugs.launchpad.net/snapcraft/+bug/1727425
        # --elopio - 2017-10-25
    )

    def __init__(self, command, app):
        super().__init__(command=command, app=app)


class InvalidContainerRemoteError(SnapcraftError):

    fmt = (
        "Failed to use LXD remote: "
        "{remote!r} is not a valid name.\n"
        "Use a LXD remote without colons, spaces and slashes in the name.\n"
    )

    def __init__(self, remote):
        super().__init__(remote=remote)


class InvalidDesktopFileError(SnapcraftError):

    fmt = (
        'Failed to generate desktop file: '
        'Invalid desktop file {filename!r}: {message}.'
        # FIXME include how to fix each of the possible desktop file errors.
        # https://bugs.launchpad.net/snapcraft/+bug/1727435
        # --elopio - 2017-10-25
    )

    def __init__(self, filename, message):
        super().__init__(filename=filename, message=message)


class SnapcraftPartMissingError(SnapcraftError):

    fmt = (
        'Failed to get part information: '
        'Cannot find the definition for part {part_name!r}. '
        'If it is a remote part, run `snapcraft update` '
        'to refresh the remote parts cache. '
        'If it is a local part, make sure that it is defined in the '
        '`snapcraft.yaml`.'
    )


class PartNotInCacheError(SnapcraftError):

    fmt = (
        'Failed to get remote part information: '
        'Cannot find the part name {part_name!r} in the cache. '
        'If it is an existing remote part, run `snapcraft update` and try '
        'again. If it has not been defined, consider going to '
        'https://wiki.ubuntu.com/snapcraft/parts to add it.'
    )


class PluginError(SnapcraftError):

    fmt = (
        'Failed to load plugin: '
        '{message}'
        # FIXME include how to fix each of the possible plugin errors.
        # https://bugs.launchpad.net/snapcraft/+bug/1727484
        # --elopio - 2017-10-25
    )

    def __init__(self, message):
        super().__init__(message=message)


class SnapcraftPartConflictError(SnapcraftError):

    fmt = (
        'Failed to stage: '
        'Parts {other_part_name!r} and {part_name!r} have the following '
        'files, but with different contents:\n'
        '{file_paths}\n\n'
        'Snapcraft offers some capabilities to solve this by use of the '
        'following keywords:\n'
        '    - `filesets`\n'
        '    - `stage`\n'
        '    - `snap`\n'
        '    - `organize`\n\n'
        'To learn more about these part keywords, run '
        '`snapcraft help plugins`.'
    )

    def __init__(self, *, part_name, other_part_name, conflict_files):
        spaced_conflict_files = ('    {}'.format(i) for i in conflict_files)
        super().__init__(part_name=part_name,
                         other_part_name=other_part_name,
                         file_paths='\n'.join(sorted(spaced_conflict_files)))


class MissingCommandError(SnapcraftError):

    fmt = (
        'Failed to run command: '
        'One or more packages are missing, please install:'
        ' {required_commands!r}'
    )

    def __init__(self, required_commands):
        super().__init__(required_commands=required_commands)


class InvalidWikiEntryError(SnapcraftError):

    fmt = (
        'Invalid wiki entry: '
        '{error!r}'
        # FIXME include how to fix each of the possible wiki errors.
        # https://bugs.launchpad.net/snapcraft/+bug/1727490
        # --elopio - 2017-10-25
    )

    def __init__(self, error=None):
        super().__init__(error=error)


class MissingGadgetError(SnapcraftError):

    fmt = (
        'Failed to generate snap metadata: '
        'Missing gadget.yaml file.\n'
        'When creating gadget snaps you are required to provide a gadget.yaml '
        'file\n'
        'in the root of your snapcraft project\n\n'
        'Read more about gadget snaps and the gadget.yaml on:\n'
        'https://github.com/snapcore/snapd/wiki/Gadget-snap')


class PluginOutdatedError(SnapcraftError):

    fmt = 'This plugin is outdated: {message}'

    def __init__(self, message):
        super().__init__(message=message)


class RequiredCommandFailure(SnapcraftError):

    fmt = '{command!r} failed.'


class RequiredCommandNotFound(SnapcraftError):

    fmt = '{cmd_list[0]!r} not found.'


class RequiredPathDoesNotExist(SnapcraftError):

    fmt = 'Required path does not exist: {path!r}'


class SnapcraftPathEntryError(SnapcraftError):

    fmt = (
        'Failed to generate snap metadata: '
        'The path {value!r} set for {key!r} in {app!r} does not exist. '
        'Make sure that the files are in the `prime` directory.'
    )


class InvalidPullPropertiesError(SnapcraftError):

    fmt = (
        'Failed to load plugin: '
        'Invalid pull properties specified by {plugin_name!r} plugin: '
        '{properties}'
        # TODO add a link to some docs about pull properties?
        # --elopio - 2017-10-25
    )

    def __init__(self, plugin_name, properties):
        super().__init__(plugin_name=plugin_name, properties=properties)


class InvalidBuildPropertiesError(SnapcraftError):

    fmt = (
        'Failed to load plugin: '
        'Invalid build properties specified by {plugin_name!r} plugin: '
        '{properties}'
        # TODO add a link to some docs about build properties?
        # --elopio - 2017-10-25
    )

    def __init__(self, plugin_name, properties):
        super().__init__(plugin_name=plugin_name, properties=properties)


class StagePackageDownloadError(SnapcraftError):

    fmt = (
        'Failed to fetch stage packages: '
        'Error downloading packages for part {part_name!r}: {message}.'
    )

    def __init__(self, part_name, message):
        super().__init__(part_name=part_name, message=message)


class OsReleaseIdError(SnapcraftError):

    fmt = 'Unable to determine host OS ID'


class OsReleaseNameError(SnapcraftError):

    fmt = 'Unable to determine host OS name'


class OsReleaseVersionIdError(SnapcraftError):

    fmt = 'Unable to determine host OS version ID'


class OsReleaseCodenameError(SnapcraftError):

    fmt = 'Unable to determine host OS version codename'


class InvalidContainerImageInfoError(SnapcraftError):

    fmt = 'Error parsing the container image info: {image_info}'

    def __init__(self, image_info):
        super().__init__(image_info=image_info)


class PatcherError(SnapcraftError):

    fmt = (
        '{elf_file!r} cannot be patched to function properly as a classic '
        'snap: {message}')

    def __init__(self, *, elf_file, message):
        super().__init__(elf_file=elf_file, message=message)
