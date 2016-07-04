# Introduction

[Evernote](http://www.evernote.com) and [1Writer](http://1writerapp.com) are two note taking apps. Evernote
focuses more on giving the end user rich text and the ability to upload
voice clips and images for OCR. 1Writer on the other hand is basically
a markdown based plain text editor for iOS devices.

This package installs a script to help you migrate from Evernote into
markdown files, keeping some metadata information for convenient use
with 1Writer.  The script will take an Evernote ``enex`` export and turn it into 
a directory of ``md`` files.

The html that is provided by Evernote is processed by the [html2text](http://pypi.python.org/pypi/html2text/)
library. This transforms the html into [Markdown](http://daringfireball.net/projects/markdown/). The 1Writer application web UI
supports previewing notes in Markdown, so this works out nicely.

## Installation

You can easily install this package using ``easy_install`` or ``pip`` as
follows (preferably in a virtualenv):

    $ pip install -U ever21writer

## Development Installation

Clone this repository with ``git``:

    $ git clone https://github...

Enter the code directory:

    $ cd ever21writer

Install live preserving local changes to the code:

    $ pip install -e .

## Usage

Once it is installed, you will have a new executable available to you.
Before you can run the conversion, you will need to export your notes.
This can be done from the desktop client. You can select the notes you
want to export, then ``Export Notes to Archive...``, and select the
``enex`` format.

Once you have that, you can run the script on the file setting the ``--output``
to a directory and using ``1writer`` as the parameter to ``--format``:

    $ ever2simple my_evernote.enex --output 1writer_dir --format 1writer

That will output each note in a ``*.md`` file named by creation date into the
``1writer_dir`` directory (creating it if it doesn't exist).

All you need is to put this directory into your Dropbox or iCloud accont for
synchornization, and to add this directory in your 1Writer app.


## Metadata saved from Evernote

The following metadata is saved from Evernote to the header of the output
``*.md`` files: 

 - tags as a list of hashtags
 - source URL of the note if any
 - creation date of the note


This is how a note will look like in the application in preview mode. 

![screenshot1](screenshots/1.png =250x)

As 1Writer makes use of hashtags you can search and browse notes using this information. 
Make sure that you have turned this feature on in 1Writer settings.

![screenshot2](screenshots/2.png =250x)

1Writer also supports autocompletion of hashtags.

![screenshot3](screenshots/3.png =250x)

Notes
-----

  - For using Evernote tags as hashtags, make sure you have your Evernote tags are named 
    the way they will be valid as hashtags. The rules are simple: no spaces, no special chars, 
    don't start with or use only numbers. The script adds the preceding ``#`` to your tags.
    See [this](https://www.hashtags.org/featured/what-characters-can-a-hashtag-include/) for more information
  - You should turn on the support for hashtags in 1Writer app for using them.
  - 1Writer looks for your whole note for hashtags when the feature is on so if your note body contains
    hashtag-like words they will show in the app as well.


Command Line Help
-----------------

The help given by running ``ever2simple -h``:


    usage: ever2simple [-h] [-o OUTPUT] [-f {json,csv,dir}] enex-file

    Convert Evernote.enex files to Markdown

    positional arguments:
      enex-file             the path to the Evernote.enex file

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            the path to the output file or directory, leave black
                            to output to the terminal (stdout) (default: None)
      -f {json,csv,dir}, --format {json,csv,dir}
                            the output format, json, csv or a directory (default:
                            json)


Notes and Caveats
-----------------

- Simplenote no longer supports JSON and CSV imports, only text files via
  Dropbox.

- Exporting to a directory will not preserve tags in the notes.

- This does not handle any attachments since simplenote doesn't support
  them. This script does not ignore the note that has attachments. This
  may make for some strange notes being imported with little to no text.

- Evernote's export looks like those horrific Microsoft Word html
  exports. You may want to cleanse the ``content`` data a bit before
  running the script. This is left as an exercise for the user.

- The notes in Evernote randomly contain unicode characters that aren't
  really harmful to you today, but may bite you in the rear later. This
  script just passes the buck, no extra cleansing of the text is done.
  The oddest character is a unicode space, why on earth do we need
  unicode spaces in our notes?1?!

