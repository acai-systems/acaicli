from datetime import datetime
from typing import List
from enum import Enum
from pprint import pprint
from acaisdk.utils.utils import bytes_to_size


class Alignment(Enum):
    LEFT = '{{:{}}}'
    RIGHT = '{{:>{}}}'


class PrettyPrint:
    @staticmethod
    def single_col(data: List, lexi_sort=False):
        if lexi_sort:
            data = sorted(data)
        for l in data:
            print(l)

    @staticmethod
    def list_with_meta(file_set, file_ids: List[str], files_meta: List,
                       human_readable_size=True):
        """
        :param file_set:
        :param human_readable_size:
        :param file_ids:
        :param files_meta: expects a list of meta dicts, one dict per file
        :return:
        """
        sorted_file_ids = PrettyPrint.sort_by_type(file_ids)
        id_to_meta = {d['_id']: d for d in files_meta}  # type: dict

        # Columns: FilePath:Version, size, createdBy, createdAt
        cols = [
            ['[{}]'.format(file_set) if file_set else '[/]',
             'size',
             'user',
             'created']
        ]
        align = [Alignment.LEFT,
                 Alignment.RIGHT,
                 Alignment.RIGHT,
                 Alignment.RIGHT]

        # Maybe some file_ids does not have meta
        for fid in sorted_file_ids:
            if fid in id_to_meta:
                size = str(id_to_meta[fid]['__size__'])
                if human_readable_size:
                    size = bytes_to_size(int(size))
                uid = str(id_to_meta[fid]['__creator_id__'])
                created_at = id_to_meta[fid]['__create_time__'] // 1000
                ts = datetime \
                    .utcfromtimestamp(created_at) \
                    .strftime('%Y-%m-%d %H:%M:%S')
                cols.append([fid, size, uid, ts])
            else:
                cols.append([fid, '-', '-', '-'])

        PrettyPrint.aligned_print(cols, align)

    @staticmethod
    def aligned_print(rows: List[List[str]],
                      alignment: List[Alignment]):
        # Loop and set max column width
        max_col_width = [0, 0, 0, 0]
        for row in rows:
            for i, c in enumerate(row):
                max_col_width[i] = max(max_col_width[i], len(c))
        # Print
        template = '  '.join([alignment[i].value.format(w)
                              for i, w in enumerate(max_col_width)])
        for r in rows:
            print(template.format(*r))

    @staticmethod
    def job(j):
        print('Registered job id: {}'.format(j.id))
        pprint(dict(j.dict))

    @staticmethod
    def sort_by_type(file_ids):
        dirs = [f for f in file_ids if f.endswith('/')]
        files = [f for f in file_ids if not f.endswith('/')]
        return sorted(dirs) + sorted(files)

    @staticmethod
    def print(content):
        pprint(content)
