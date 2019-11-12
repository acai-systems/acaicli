from acaisdk.utils.exceptions import *
from .cliutils import *
from acaisdk.file import File
from acaisdk.fileset import FileSet
from acaisdk.project import Project
from acaisdk.utils.utils import debug
from acaisdk.job import Job
from acaisdk.meta import Meta, Condition
from .prettyprint import PrettyPrint
import os
from typing import List
from enum import Enum, auto


class Command:
    def __init__(self, args):
        self.args = args

    def process(self):
        pass


class UploadCommand(Command):
    def process(self):
        paths = self.args.file_paths
        # Allow additional input from pipe in
        if '-' in paths[:-1]:
            paths.remove('-')
            more_inputs = [l.strip() for l in sys.stdin if l.strip()]
            paths = more_inputs + paths

        l_r_mapping, ignored_paths = \
            File.convert_to_file_mapping(paths[:-1], paths[-1])

        if self.args.dry_run:
            print_info('[DRY RUN] Files to be uploaded:')
            for l, r in l_r_mapping:
                print('{} => {}'.format(l, r))
            if ignored_paths:
                print_warn('[DRY RUN] Files to be ignored (inaccessible):')
                for l in ignored_paths:
                    print(l)
        else:
            result = File.upload(l_r_mapping)
            if self.args.fileset:
                r = result.as_new_file_set(self.args.fileset)
                print(r)
            print("results:")
            print(result)


class DownloadCommand(Command):
    def process(self):
        # If
        # self.args.paths
        # TODO: I was here
        pass


class CreateCommand(Command):
    def process(self):
        if self.args.create == 'project':
            r = Project.create_project(self.args.project,
                                       self.args.admin_token,
                                       self.args.user)
            print(r)
        elif self.args.create == 'user':
            r = Project.create_user(self.args.project,
                                    self.args.admin_token,
                                    self.args.user)
            print('User {} (id {}) created. Use\n'.format(self.args.user,
                                                          r['id']))
            print(color_msg('\rexport ACAI_TOKEN={}'.format(r['user_token']),
                            color=Colors.BLUE))
            print('\nto activate')
        elif self.args.create == 'fileset':
            r = FileSet.create_file_set(self.args.fileset,
                                        self.args.remote_paths)
            print(r)


class JobCommand(Command):
    def process(self):
        if self.args.action == 'run':
            attrs = {
                'name': self.args.name,
                'v_cpu': self.args.vcpu,
                'memory': self.args.mem,
                'gpu': self.args.gpu,
                'command': self.args.command,
                'container_image': self.args.image,
                'input_file_set': self.args.input_fileset,
                'output_path': self.args.output_path,
                'code': self.args.code,
                'description': self.args.description,
            }
            j = Job().with_attributes(attrs).register()
            PrettyPrint.job(j)
            j.run()
        elif self.args.action == 'tag':
            MetaCommand.tag(MetaCommand.EntityType.JOB, self.args)
        elif self.args.action == 'untag':
            MetaCommand.untag(MetaCommand.EntityType.JOB, self.args)
        elif self.args.action == 'find':
            MetaCommand.find(MetaCommand.EntityType.JOB, self.args)


class FileSetCommand(Command):
    def process(self):
        if self.args.action == 'ls':
            if not self.args.fileset:
                r = FileSet.list_file_sets()
                PrettyPrint.single_col(r, lexi_sort=True)
            else:
                r = FileSet.list_file_set_content(self.args.fileset)
                with_meta = self.args.with_meta
                fs_msg = '[FILESET] {}'.format(r['id'])
                print(fs_msg)
                ListCommand.list_file_set_content(r['id'], with_meta)
        elif self.args.action == 'get':
            # Download a fileset to a folder
            FileSet.download_file_set(self.args.fileset,
                                      self.args.output,
                                      self.args.force)
        elif self.args.action == 'versions':
            r = FileSet.list_file_set_versions(self.args.fileset)
            for d in r:
                print(d['id'])
        elif self.args.action == 'tag':
            MetaCommand.tag(MetaCommand.EntityType.FILESET, self.args)
        elif self.args.action == 'untag':
            MetaCommand.untag(MetaCommand.EntityType.FILESET, self.args)
        elif self.args.action == 'find':
            MetaCommand.find(MetaCommand.EntityType.FILESET, self.args)


class FileCommand(Command):
    def process(self):
        if self.args.action == 'ls':
            if not self.args.directory:
                self.args.directory = '/'
            r = File.list_dir(self.args.directory)
            for d in r:
                path = d['path']
                if d['is_dir']:
                    path += '/'
                print(path)
        elif self.args.action == 'versions':
            r = File.list_file_versions(self.args.file)
            for path in r:
                print(path)
        elif self.args.action == 'tag':
            MetaCommand.tag(MetaCommand.EntityType.FILE, self.args)
        elif self.args.action == 'untag':
            MetaCommand.untag(MetaCommand.EntityType.FILE, self.args)
        elif self.args.action == 'find':
            MetaCommand.find(MetaCommand.EntityType.FILE, self.args)


class MetaCommand(Command):
    class EntityType(Enum):
        JOB = auto()
        FILE = auto()
        FILESET = auto()

    @staticmethod
    def tag(entity_type: EntityType, args):
        MetaCommand._modify_meta(entity_type, args)

    @staticmethod
    def untag(entity_type: EntityType, args):
        MetaCommand._remove_meta(entity_type, args)

    @staticmethod
    def find(entity_type: EntityType, args):
        constraints = []
        if args.max:
            constraints.append(Condition(args.max).max())
        if args.min:
            constraints.append(Condition(args.min).min())
        if args.value:
            for kv in args.value:
                k, v = kv.split('=')
                constraints.append(Condition(k).value(v))
        if args.number_value:
            for kv in args.number_value:
                k, v = kv.split('=')
                v = float(v)
                constraints.append(Condition(k).value(v))
        if args.regex_value:
            for kv in args.regex_value:
                k, v = kv.split('=')
                constraints.append(Condition(k).value(v).re())
        if args.range:
            for k_range in args.range:
                k, r = k_range.split('=')
                left, right = map(float, r.split('-'))
                constraints.append(Condition(k).range(left, right))

        find_methods = {
            MetaCommand.EntityType.JOB: Meta.find_job,
            MetaCommand.EntityType.FILE: Meta.find_file,
            MetaCommand.EntityType.FILESET: Meta.find_file_set
        }
        r = find_methods[entity_type](*constraints)
        PrettyPrint.print(r['data'])

    @staticmethod
    def _modify_meta(entity_type: EntityType, args):
        tags = args.tags if args.tags else []
        kv_pairs = {}
        if args.kv_pairs:
            for x in args.kv_pairs:
                try:
                    k, v = x.split('=')
                    kv_pairs[k] = v
                except:
                    raise AcaiException('KV pairs should be separated by a "="')
        if args.num_kv_pairs:
            for x in args.num_kv_pairs:
                try:
                    k, v = x.split('=')
                    kv_pairs[k] = float(v)
                except:
                    raise AcaiException('KV pairs should be separated by a "="')
        if not tags and not kv_pairs:
            return

        methods = {
            MetaCommand.EntityType.JOB: Meta.update_job_meta,
            MetaCommand.EntityType.FILE: Meta.update_file_meta,
            MetaCommand.EntityType.FILESET: Meta.update_file_set_meta
        }

        r = methods[entity_type](args.entity, tags, kv_pairs)

        print(r['status'])

    @staticmethod
    def _remove_meta(entity_type: EntityType, args):
        tags = args.tags if args.tags else []
        keys = args.keys if args.keys else []
        if not tags and not keys:
            return

        methods = {
            MetaCommand.EntityType.JOB: Meta.del_job_meta,
            MetaCommand.EntityType.FILE: Meta.del_file_meta,
            MetaCommand.EntityType.FILESET: Meta.del_file_set_meta
        }
        r = methods[entity_type](args.entity, tags, keys)

        print(r)


class ListCommand(Command):
    def process(self):
        v = self.args.dir_or_file_set
        with_meta = self.args.with_meta
        if v and v.startswith('@'):
            file_set = v[1:]
            if len(file_set) == 0:
                # If only an "@" is given, list all filesets
                r = FileSet.list_file_sets()
                PrettyPrint.single_col(r, lexi_sort=True)
            else:
                ListCommand.list_file_set_content(file_set, with_meta)
        else:
            try:
                ListCommand.list_dir(v, with_meta)
            except RemoteException:
                # Folder does not exist, maybe it is a file
                try:
                    r = Meta.get_file_meta([v])
                    PrettyPrint.print(r['data'][0])
                except RemoteException:
                    print('{} does not exist'.format(v))


    @staticmethod
    def list_dir(dir_path, with_meta:bool):
        if not dir_path:
            # Nothing given, list root directory.
            dir_path = '/'
        r = File.list_dir(dir_path)
        explicit_paths = []

        for d in r:
            if d['is_dir']:
                path = d['path'] + '/'
                explicit_paths.append(path)
            else:
                versioned_path = ':'.join([d['path'], str(d['version'])])
                if dir_path == '/':
                    dir_path = ''
                explicit_paths.append(os.path.join(dir_path, versioned_path))

        ListCommand._print_files(dir_path, explicit_paths, with_meta=with_meta)

    @staticmethod
    def list_file_set_content(file_set, with_meta: bool):
        r = FileSet.list_file_set_content(file_set)
        ListCommand._print_files(r['id'], r['files'], with_meta)

    @staticmethod
    def _print_files(file_set_or_dir, file_paths, with_meta: bool) -> None:
        if with_meta:
            paths_without_dir = [p for p in file_paths if not p.endswith('/')]
            meta = []
            if paths_without_dir:
                r = Meta.get_file_meta(*paths_without_dir)
                meta = r['data']
            # By default, sort by file name
            PrettyPrint.list_with_meta(file_set_or_dir,
                                       sorted(file_paths),
                                       meta)
        else:
            PrettyPrint.single_col(file_paths, lexi_sort=True)
