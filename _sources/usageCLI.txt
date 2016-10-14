Running the Command Line Script
-------------------------------

To move all the files in a directory into a Medusa package follow these steps.

1) Open a command prompt/terminal.
2) Type "packagemedusa" followed by the path to the directory and a path to save the new packaged content.

You are done.

For example... ::

        packagemedusa /Users/hborcher/Documents/dummy /Users/hborcher/Documents/mynewpackage

It's that simple!

.. NOTE:: While this documentation should be up to date, if there is any question about how to use the current version
          \ installed, you can always type "packagemedusa -h" into a command prompt. This will provide the usage and all
          \ the options for the currently install version of the script. ::


            $ packagemedusa -h

            usage: packagemedusa [-h] [--copy] source destination

            positional arguments:
              source       Directory for files to be sorted
              destination  Directory to put the new files

            optional arguments:
              -h, --help   show this help message and exit
              --copy       Copy files instead of moving them.

