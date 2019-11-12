import sys
import argparse
from typing import Tuple, Dict
from .cliutils import print_err
from .commands import *


def _has_level2_commands(func):
    def wrapper(o) -> argparse.Namespace:
        sys_argv_backup = sys.argv
        sys.argv = sys.argv[1:]
        args = func(o)
        sys.argv = sys_argv_backup
        return args

    return wrapper


def _level2_checker(parser):
    if len(sys.argv) < 2:
        parser.print_help()
        exit(2)


def _level1_checker(parser):
    if len(sys.argv) < 3:
        parser.print_help()
        exit(2)


class ArgumentLoader:
    def __init__(self):
        self.file_name = 'acai'
        self.services = {
            'create': (self._create, CreateCommand),
            'put': (self._put, UploadCommand),
            'fileset': (self._fileset, FileSetCommand),
            'job': (self._job, JobCommand),
            'file': (self._file, FileCommand),
            'ls': (self._list, ListCommand)
        }
        self.sys_argv_backup = sys.argv
        sys.argv = sys.argv[:2]
        formatter_class = lambda prog: MyFormatter(
            prog, max_help_position=50, width=100)
        self.main_parser = argparse.ArgumentParser(
            formatter_class=formatter_class)
        self.main_parser.add_argument(dest='service',
                                      choices=self.services.keys())

    def parse(self) -> Tuple[argparse.Namespace, Command]:
        level1_args = self.main_parser.parse_args()
        sys.argv = self.sys_argv_backup
        args = self.services[level1_args.service][0]()
        action = self.get_action(args)
        return args, action

    def get_action(self, args: argparse.Namespace) -> Command:
        return self.services[sys.argv[1]][1](args)

    @_has_level2_commands
    def _create(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(usage=self.file_name)
        parser.usage += ' create'
        subparsers = parser.add_subparsers(dest='create')

        create_project_parser = subparsers.add_parser('project')
        create_project_parser.add_argument(
            '-p', '--project',
            dest='project',
            required=True,
            metavar='PROJECT_NAME',
            help='name of the new project.'
        )
        create_project_parser.add_argument(
            '-t', '--admin_token',
            dest='admin_token',
            required=True,
            metavar='ADMIN_TOKEN',
            help='admin token '
                 '(EmDlCTBF1ppONSciYVd03M9xkmF6hFqW).'
        )
        create_project_parser.add_argument(
            '-u', '--user',
            dest='user',
            required=True,
            metavar='USER_NAME',
            help='name of the new project administrator.'
        )

        create_user_parser = subparsers.add_parser('user')
        create_user_parser.add_argument(
            '-p', '--project',
            dest='project',
            required=True,
            metavar='PROJECT_NAME',
            help='name of the project to create user under.'
        )
        create_user_parser.add_argument(
            '-u', '--user',
            dest='user',
            required=True,
            metavar='USER_NAME',
            help='name of the new user.'
        )
        create_user_parser.add_argument(
            '-t', '--admin_token',
            dest='admin_token',
            required=True,
            metavar='PROJECT_ADMIN_TOKEN',
            help='project admin token, '
                 'obtained through project creation.'
        )

        create_fs_parser = subparsers.add_parser('fileset')
        create_fs_parser.add_argument(
            '-n', '--name',
            dest='fileset',
            required=True,
            metavar='FILESET',
            help='name of the new file set.'
        )
        create_fs_parser.add_argument(
            '-f', '--paths',
            nargs='+',
            dest='remote_paths',
            required=True,
            metavar='REMOTE_PATHS',
            help='remote file/directory paths to include in the new file set.'
        )
        _level2_checker(parser)
        return parser.parse_args()

    def _put(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        upload_parser = subparsers.add_parser(
            'put',
            usage='acai put [OPTIONS] '
                  'LOCAL_FILE [LOCAL_FILE ...] REMOTE_DIR/\n       '
                  'acai put [OPTIONS] '
                  'LOCAL_FILE REMOTE_FILE\n       '
                  'acai put [OPTIONS] '
                  'LOCAL_DIR/ REMOTE_DIR/'
        )
        upload_parser.add_argument(
            nargs='+',
            dest='file_paths',
            metavar='FILE_PATH',
            help='Local file/directory path or '
                 'remote file/directory path.'
        )
        upload_parser.add_argument(
            '-d', '--dry_run',
            dest='dry_run',
            action='store_true',
            default=False,
            help='If not sure about the command behavior, '
                 'use this option to list the actions '
                 'without actually uploading.'
        )
        upload_parser.add_argument(
            '--fileset',
            dest='fileset',
            default=None,
            help='Put uploaded files into a fileset.'
        )

        args = parser.parse_args()
        if len(args.file_paths) < 2:
            print_err('Must provide at least 1 local and 1 remote '
                      'paths/directories.')
            upload_parser.print_help()
            exit(2)
        return args

    def _get(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        download_parser = subparsers.add_parser(
            'get',
            usage='acai get [OPTIONS] '
                  'REMOTE_FILE_1 REMOTE_FILE_2 [REMOTE_FILE_3 ...] LOCAL_DIR/'
                  '\n       '
                  'acai get [OPTIONS] '
                  'REMOTE_FILE [LOCAL_FILE]'
                  '\n       '
                  'acai get [OPTIONS] '
                  'REMOTE_DIR/ LOCAL_DIR/'
                  '\n       '
                  'acai get @FILESET LOCAL_DIR/'
        )
        download_parser.add_argument(
            nargs='+',
            dest='paths',
            metavar='PATHS_OR_FILESET',
            help='Download remote file or directory or file set to local.'
        )
        download_parser.add_argument(
            '-d', '--dry_run',
            dest='dry_run',
            action='store_true',
            default=False,
            help='If not sure about the command behavior, '
                 'use this option to list the actions '
                 'without actually uploading.'
        )

        return parser.parse_args()

    @_has_level2_commands
    def _fileset(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(usage=self.file_name)
        parser.usage += ' fileset'
        subparsers = parser.add_subparsers(dest='action')

        list_fs_parser = subparsers.add_parser('ls')
        list_fs_parser.add_argument(
            dest='fileset',
            metavar='FILESET',
            nargs='?',
            default=None,
            help='list files in this file set. '
                 'Or list all file sets when no argument given.'
        )
        list_fs_parser.add_argument(
            '-l',
            action='store_true',
            dest='with_meta',
            default=False,
            help='Print meta data.'
        )

        get_fs_parser = subparsers.add_parser('get')
        get_fs_parser.add_argument(
            '-f', '--fileset',
            dest='fileset',
            metavar='FILESET',
            required=True,
            help='name of the file set to download.'
        )
        get_fs_parser.add_argument(
            '-o', '--output',
            dest='output',
            metavar='OUTDIR',
            required=True,
            help='name of the target local directory.'
        )
        get_fs_parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            default=False,
            help='overwrite existing files.'
        )

        list_versions_parser = subparsers.add_parser('versions')
        list_versions_parser.add_argument(
            dest='fileset',
            metavar='FILESET',
            help='list all versions of this file set'
        )

        self._add_tag_and_untag_parser(subparsers, 'fileset')
        self._add_find_parser(subparsers)

        _level2_checker(parser)
        return parser.parse_args()

    @_has_level2_commands
    def _job(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(usage=self.file_name)
        parser.usage += ' job'
        subparsers = parser.add_subparsers(dest='action')
        run_job_parser = subparsers.add_parser('run')
        run_job_parser.add_argument(
            '-n',
            dest='name',
            default=None,
            help=''
        )
        run_job_parser.add_argument(
            '-m', '--desc',
            dest='description',
            default=None,
            help=''
        )
        run_job_parser.add_argument(
            '-i', '--input_fileset',
            dest='input_fileset',
            required=True,
            help=''
        )
        run_job_parser.add_argument(
            '-o', '--output_path',
            dest='output_path',
            required=True,
            help=''
        )
        run_job_parser.add_argument(
            '--code',
            dest='code',
            required=True,
            help=''
        )
        run_job_parser.add_argument(
            '--command',
            dest='command',
            required=True,
            help=''
        )
        run_job_parser.add_argument(
            '--image',
            dest='image',
            required=True,
            help=''
        )
        run_job_parser.add_argument(
            '--gpu',
            dest='gpu',
            default='0',
            help=''
        )
        run_job_parser.add_argument(
            '--vcpu',
            dest='vcpu',
            default='0.5',
            help=''
        )
        run_job_parser.add_argument(
            '--mem',
            dest='mem',
            default='512Mi',
            help=''
        )

        self._add_tag_and_untag_parser(subparsers, 'job')
        self._add_find_parser(subparsers)

        _level2_checker(parser)
        return parser.parse_args()

    @_has_level2_commands
    def _file(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(usage=self.file_name)
        parser.usage += ' file'
        subparsers = parser.add_subparsers(dest='action')

        list_dir_parser = subparsers.add_parser('ls')
        list_dir_parser.add_argument(
            dest='directory',
            metavar='DIRECTORY',
            nargs='?',
            default=None,
            help='list files in remote directory. '
                 'Or list root directory if no argument given.'
        )

        list_versions_parser = subparsers.add_parser('versions')
        list_versions_parser.add_argument(
            dest='file',
            metavar='FILE',
            help='list all versions of this file.'
        )

        self._add_tag_and_untag_parser(subparsers, 'file')
        self._add_find_parser(subparsers)

        _level2_checker(parser)
        return parser.parse_args()

    def _list(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        list_parser = subparsers.add_parser('ls')
        list_parser.add_argument(
            nargs='?',
            dest='dir_or_file_set',
            metavar='DIRECTORY/FILESET',
            help='remote file directory or file set name.'
        )
        list_parser.add_argument(
            '-l',
            action='store_true',
            dest='with_meta',
            default=False,
            help='If print meta data.'
        )

        return parser.parse_args()

    def _add_tag_and_untag_parser(self, subparsers, command):
        entity_name_map = {
            'job': ('-j', '--job_id', 'JOB_ID', 'job', int),
            'file': ('-f', '--file', 'FILE', 'file', str),
            'fileset': ('-f', '--fileset', 'FILESET', 'file set', str)
        }

        opt, long_opt, metavar, name, id_type = entity_name_map[command]

        tag_parser = subparsers.add_parser('tag')
        tag_parser.add_argument(
            opt, long_opt,
            dest='entity',
            metavar=metavar,
            required=True,
            type=id_type,
            help='id of the {} to add metadata to.'.format(name)
        )
        tag_parser.add_argument(
            '-t', '--tags',
            dest='tags',
            metavar='TAGS',
            nargs='+',
            help='add value-only metadata to a {} '
                 '(as opposed to k-v pair metadata).'.format(name)
        )
        tag_parser.add_argument(
            '-v', '--kv_pairs',
            dest='kv_pairs',
            metavar='KEY=VALUE',
            nargs='+',
            help='add key-value pair metadata to a {}.'.format(name)
        )
        tag_parser.add_argument(
            '-n', '--num_kv_pairs',
            dest='num_kv_pairs',
            metavar='KEY=NUMBER',
            nargs='+',
            help='add key-value pair metadata to a {} where value '
                 'is a number.'.format(name)
        )

        untag_parser = subparsers.add_parser('untag')
        untag_parser.add_argument(
            opt, long_opt,
            dest='entity',
            metavar=metavar,
            required=True,
            type=id_type,
            help='id of the {} to remove metadata from.'.format(name)
        )
        untag_parser.add_argument(
            '-t', '--tags',
            dest='tags',
            metavar='TAGS',
            nargs='+',
            help='remove value-only metadata '
                 '(as opposed to k-v pair metadata).'
        )
        untag_parser.add_argument(
            '-k', '--keys',
            dest='keys',
            metavar='KEYS',
            nargs='+',
            help='remove key-value pair metadata by key.'
                 'E.g. untag -k eval_loss'
        )

    def _add_find_parser(self, subparsers):
        """This method creates a parser for "find" function for file, fileset
        and job command.
        """
        find_parser = subparsers.add_parser('find')
        find_parser.add_argument(
            '-v', '--value',
            dest='value',
            metavar='KEY=VALUE',
            nargs='+',
            help='find entity where metadata value equals to input string. '
                 'Usage: -v k1=v1 k2=v2'
        )
        find_parser.add_argument(
            '-s',
            dest='value',
            metavar='KEY=VALUE',
            nargs='+',
            help='same as -v'
        )
        find_parser.add_argument(
            '-n', '--number',
            dest='number_value',
            metavar='KEY=NUMBER',
            nargs='+',
            help='find entity where metadata value equals to input number.\n'
                 'Usage: -n k1=num1 k2=num2'
        )
        find_parser.add_argument(
            '-r', '--regex',
            dest='regex_value',
            metavar='KEY=REGEX',
            nargs='+',
            help='find entity where metadata value matches input regex.\n'
                 'Usage: -r k1=regex1 k2=regex2'
        )
        find_parser.add_argument(
            '--max',
            dest='max',
            metavar='KEY',
            help='find entity with maximum value at KEY.'
        )
        find_parser.add_argument(
            '--min',
            dest='min',
            metavar='KEY',
            help='find entity with minimum value at KEY.'
        )
        find_parser.add_argument(
            '--range',
            dest='range',
            metavar='KEY=FROM-TO',
            nargs='+',
            help='find entity where the value at KEY is within '
                 'a number range. Left exclusive, right inclusive.\n'
                 'E.g. --range  loss=0.5-1.0  __size__=1024-65535'
        )


class MyFormatter(argparse.HelpFormatter):
    """Formats the CLI help info.

    Corrected _max_action_length for the indenting of subactions

    Directly copied from
    https://stackoverflow.com/questions/32888815/max-help-position-is-not-works-in-python-argparse-library
    """

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent
            for sub_action in self._iter_indented_subactions(action):
                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(sub_action))

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])


if __name__ == "__main__":
    print(ArgumentLoader().parse())
