## This isn't finished yet
##### Stuff that works:
* Creating a public link
* Deleting a public link
* Password protection
* Editing an existing user/group share
* Deleting an existing user/group share
* Setting an expiration date
* Adding a new user/group share

##### Stuff that doesn't work yet:
* ~~Adding a new user/group share~~
* ~~Setting an expiration date~~
* Handling of files that aren't inside the ownCloud share directory
* ~~Support for non-Linux operating systems~~

## ownCloud-share-tools

ownCloud share tools is an set of tools that provide access to the ownCloud OCS Share API. In this repository you will find the command line client, GUI and Python library for interfacing with ownCloud shares.

## Using the GUI

The GUI is designed to be used as a file browser action. Most file browsers allow you to add custom actions, for example to add the GUI to Thunar go to edit, configure custom actions, click add then in the command box enter

`python3 ocssharetools.py gui --user YourUserName --pass YourPassword --url http://example.com/owncloud gui --path %F`

All the other text boxes can be set to whatever you want.

You will then be able to right click on a file in thunar, and select your custom action, which will invoke the GUI

## Using the CLI
Using the CLI is very simple, just run python3 ocssharetools.py --help for more details. It is fully documented.
