import os
import shutil
import argparse

import sys

import MedusaPackager
from pkg_resources import get_distribution, DistributionNotFound


class Processor:
    """
    Abstract base class for any addition type of jobs that need to be done. Intended to make building addition
    operations from a factory function.
    """

    def process(self, source, destination):
        pass


class MoveWorker(Processor):
    """
    Used for moving files.
    """

    def process(self, source, destination):
        """
        Used for moving files.
        :param source: File to be moved.
        :param destination: Destination path for the file to be move to.
        """
        shutil.move(source, destination)


class CopyWorker(Processor):
    """
    Used for copy files.
    """

    def process(self, source, destination):
        """
        Used for copy files.
        :param source: File to be copied.
        :param destination: Destination path for the file to be copied to.
        """
        shutil.copy2(source, destination)


def find_arg_problems(args):
    """
    Check to see if any problems with the arguments and yield them
    :param args:
    :yields: String containing error messages about any problems found
    """
    if not os.path.exists(args.source):
        yield "\"{}\" is not a valid source.".format(args.source)
    if not os.path.exists(args.destination):
        yield "\"{}\" is not a valid destination.".format(args.destination)


def build_parser():
    try:
        package_metadata = get_distribution(__package__)
        version = package_metadata.version
        for line in package_metadata.get_metadata_lines(name="PKG-INFO"):
            if line.startswith("Summary:"):
                description = line
                break
        else:
            description = "error: Unable to load description information"
    except DistributionNotFound as e:
        description = "error: Unable to load description information"
        version="unknown"
    except FileNotFoundError as e:
        description = "error: Unable to load description information"
        version="unknown"
    parser = argparse.ArgumentParser(description)
    parser.add_argument("--version",
                                   action="version",
                                   version=version)

    # process_group = command_group.add_argument_group()
    parser.add_argument('source', help="Directory for files to be sorted")
    parser.add_argument('destination', default=os.getcwd(), help="Directory to put the new files")
    parser.add_argument('--copy', action="store_true", help="Copy files instead of moving them.")
    # process_group.add_argument('source', help="Directory for files to be sorted")
    # process_group.add_argument('destination', default=os.getcwd(), help="Directory to put the new files")
    # process_group.add_argument('--copy', action="store_true", help="Copy files instead of moving them.")

    return parser


def setup():
    parser = build_parser()
    args = parser.parse_args()
    problems = list(find_arg_problems(args))
    if len(problems) > 0:
        parser.print_help(file=sys.stderr)
        print("\nError:", file=sys.stderr)
        for problem in problems:
            print(problem, file=sys.stderr)

        exit(1)
    return args


def get_worker(args):
    """
    Factory function that parses the arguments and returns that type of job that needs to be performed. Whether it's
    a copy or a move.
    :param args:
    :return:
    """
    if args.copy:
        return CopyWorker()
    else:
        return MoveWorker()
    pass


def main():
    args = setup()
    dest = args.destination
    unsorted_data = MedusaPackager.find_package_files(args.source)

    # use factory method to get the right type of copy or move based on the argument parser
    worker = get_worker(args)

    # organize all the files into a groups based on the name left of the dash
    packages = unsorted_data.split_items(MedusaPackager.dash_grouper)
    for i, package in enumerate(sorted(packages, key=lambda x: x.package_name)):

        # Sort files into types based on their parrent folder, access, preservation
        sorted_data = package.sorted()

        # the new path for each package takes the name of the group.
        # This is decided based on the left side of the dash in the file names
        new_package_path = os.path.join(dest, sorted_data.package_name)
        print("Package ({}/{}): Packaging files in \"{}\"".format(i + 1, len(packages), new_package_path))

        # If there isn't an empty folder for the new package, create one
        if not os.path.exists(new_package_path):
            MedusaPackager.create_empty_package(new_package_path)

        # For every file that needs to be moved or copied, provide the source file name,
        # and the new location
        jobs = list(sorted_data.generate_deployment(dest))
        # files = list(get_files(sorted_data, new_package_path))
        for i2, job in enumerate(jobs):
            print("File {} of {}: \"{}\"".format(i2 + 1, len(jobs), job.destination))

            # based on the factory method, use the correct worker to copy or move
            worker.process(job.source, job.destination)
        print("")
        pass
    print("All Done")


if __name__ == '__main__':
    main()
