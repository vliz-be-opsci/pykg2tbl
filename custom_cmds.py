import io
import os
import subprocess
import sys
import unittest
from shutil import rmtree

from setuptools import Command

# Fixed Package meta-data.
NAME = "pykg2tbl"

TEST_FOLDER = "tests"
TEST_PATTERN = "test_*.py"


# Dynamic Packge meta-data  - read from different local files
here = os.path.abspath(os.path.dirname(__file__))
# Load the package's __version__.py module as a dictionary.
about = {}
with io.open(os.path.join(here, NAME, "__version__.py")) as f:
    exec(f.read(), about)


# define specific setup commands
class CommandBase(Command):
    """ "AbstractBase for our own commands"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))


class TestCommand(CommandBase):
    """ "Support setup.py test"""

    description = "Perform the tests"

    def run(self):
        self.status("Discovering tests with pattern %s in folder %s" % (TEST_PATTERN, TEST_FOLDER))
        suite = unittest.TestLoader().discover(TEST_FOLDER, pattern=TEST_PATTERN)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        exit(0 if result.wasSuccessful() else 1)


class UploadCommand(CommandBase):
    """Support setup.py upload."""

    description = "Build and publish the package."

    def run(self):
        try:
            self.status("Removing previous builds")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine")
        os.system("twine upload dist/*")

        sys.exit()


class ReleaseCommand(CommandBase):
    """Support setup.py upload."""

    description = "Tag the package."

    def run(self):
        self.version_tag = "v" + about["__version__"]
        self.status("Commiting this build...")
        os.system('git commit -am "Setup.py commit for version {0}" '.format(self.version_tag))

        self.status("Tagging this build with {0}".format(self.version_tag))
        try:
            subprocess.run(["git", "tag", self.version_tag], check=True)
            self.status("Git push")
            os.system("git push --tags")
        except subprocess.CalledProcessError:
            self.status("Rolling back last commit...")
            os.system("git reset --soft HEAD~1")
            # Delete old tag. This is not safe, needs to be done when
            #   pushing a new version only...
            # os.system('git tag -d {0}'.format(self.version_tag))
        sys.exit()
