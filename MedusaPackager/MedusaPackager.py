import os
from enum import Enum
import itertools
from pprint import pprint

from collections import defaultdict, namedtuple

VALID_IMAGE_EXTENSIONS = [".tif", ".jp2"]
SYSTEM_FILES = ["Thumbs.db"]

package_packet = namedtuple("package_packet", ['source', 'destination'])

class FileTypes(Enum):
    ACCESS = "ACCESS"
    PRESERVATION = "PRESERVATION"
    IGNORED = "IGNORED"


def identify_filetype(path):
    """
    Identifies a file as an access or preservation file based on the file's parent directory
    :param path:
    :return: Enum FileType
    """
    path, filename = os.path.split(path)
    parent = os.path.normpath(path).split(os.path.sep)[-1]
    if parent == "access":
        return FileTypes.ACCESS
    elif parent == "preservation master":
        return FileTypes.PRESERVATION



def create_empty_package(name):
    """
    Creates a new directory with the given file name. Within the folder it generates 2
    folders: "access" and "preservation"
    :param name: root folder name for the package
    """

    os.mkdir(name)
    os.mkdir(os.path.join(name, "preservation"))
    os.mkdir(os.path.join(name, "access"))


class MedusaPackageData:
    def __init__(self):
        self.access_files = []
        self.preservation_files = []
        self.ignored_files = []
        self.unsorted_files = []
        self.package_name = None

    def isBalanced(self):
        """
        Checks to see if there are equal number of access files and preservation files
        :return: Returns true if the number of preservation files match the number of access files else returns false
        """
        return len(self.access_files) == len(self.preservation_files)

    @property
    def all_files(self):
        return self.unsorted_files + self.preservation_files + self.access_files + self.ignored_files

    @property
    def all_image_files(self):
        return self.unsorted_files + self.preservation_files + self.access_files

    def __len__(self):
        return len(self.access_files) + len(self.preservation_files)

    def sorted(self, callback=identify_filetype):
        """
        Generates a new MedusaPackageData with files organized by type based on a callback function. Such as Preservation and access
        :param callback:
        :return: new MedusaPackageData with files organized
        """
        sorted_data = sort_package_by_type(self, callback)
        return sorted_data

    def split_items(self, callback):
        return list(split_items(self, callback))

    def generate_deployment(self, path):
        for file in self.access_files:
            yield package_packet(file, os.path.join(path, self.package_name, "access", os.path.basename(file)))

        for file in self.preservation_files:
            yield package_packet(file, os.path.join(path, self.package_name, "preservation", os.path.basename(file)))


def find_package_files(path)->MedusaPackageData:
    """
    Find all valid image files in a given path and create a MedusaPackageData object.
    :param path:
    :return: MedusaPackageData with found files in unsorted
    """

    new_package = MedusaPackageData()
    for root, dirs, files in os.walk(path):
        for _file in files:
            if _file in SYSTEM_FILES:
                new_package.ignored_files.append(os.path.join(root, _file))
                continue
            if os.path.splitext(_file)[1].lower() not in VALID_IMAGE_EXTENSIONS:
                new_package.ignored_files.append(os.path.join(root, _file))
                continue

            new_package.unsorted_files.append(os.path.join(root, _file))
    return new_package


def sort_package_by_type(package: MedusaPackageData, id_callback):
    """
    Used to sort files in the unsorted category and assign it to the access or preservation category
    :param package: MedusaPackageData with files to be sorted
    :param id_callback: Callback to a function that takes in a path and returns a MedusaPackager.FileType enum type
    :return: Returns a new MedusaPackageData object with the values sorted
    """
    new_package = MedusaPackageData()
    new_package.ignored_files = [x for x in package.ignored_files]
    new_package.package_name = package.package_name

    for file in package.unsorted_files:
        file_type = id_callback(file)

        if file_type == FileTypes.ACCESS:
            new_package.access_files.append(file)
        elif file_type == FileTypes.PRESERVATION:
            new_package.preservation_files.append(file)
        elif file_type == FileTypes.IGNORED:
            new_package.ignored_files.append(file)
        else:
            raise Exception("Unknown enum exception for {}".format(file))
    return new_package


def default_grouper(files):
    """
    Generator function that groups a list files by their basename.
    Use as a callback with MedusaPackageData.split_items() method.
    :param files:
    :return:
    """

    def group_filter(x):
            return os.path.basename(x)
    groups = defaultdict(list)

    for y, x in itertools.groupby(files, group_filter):
        groups[y] += x

    for g in groups.items():
        yield g


def dash_grouper(files):
    """
    Generator function that groups a list files by anything left of a slash in the filename.
    Use as a callback with MedusaPackageData.split_items() method.
    :param files:
    :return:
    """
    def group_filter(x):
        return os.path.basename(x).split("-")[0]

    groups = defaultdict(list)

    for y, x in itertools.groupby(files, group_filter):
        groups[y] += x

    for g in groups.items():
        yield g


def split_items(package, key=default_grouper):
    """
    Generator that organizes unsorted files in a MedusaPackage and yields new ones based on the key
    :param package:
    :param key: callback to sort files into categories. Defaults to sorting by basename
    :return:
    """
    items = key(package.unsorted_files)
    for item in items:
        new_package = MedusaPackageData()
        new_package.package_name = item[0]
        new_package.unsorted_files = [x for x in item[1]]
        yield new_package
