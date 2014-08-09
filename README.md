## ownCloud-share-tools

ownCloud share tools is an set of tools that provide access to the ownCloud OCS Share API. In this repository you will find the command line client, GUI and Python library for interfacing with ownCloud shares.

***

## The GUI

![](http://i.imgur.com/VQ5vG24.png)
ownCloud-share-tools running on Linux as a Thunar custom action.

The GUI is designed to be used as a file browser action.
To add the GUI to Thunar, open Thunar and click edit, configure custom actions, click add then in the command box enter

`./ocsharetools.py --user YourUserName --pass YourPassword --url http://example.com/owncloud gui --path %F`

All the other text boxes can be set to whatever you want, although setting the name to ownCloud and using the ownCloud icon is recommended.

***

## Using the CLI
```
$ ./ocsharetools.py --help
usage: ocsharetools.py [-h] --username USERNAME --password PASSWORD --url URL
                       {getshares,getshare,create,update,delete,gui} ...

Perform OCS Share API calls

positional arguments:
  {getshares,getshare,create,update,delete,gui}
                        Available commands
    getshares           get Shares from a specific file or folder
    getshare            get a single share by id
    create              create a share
    update              update a share
    delete              delete a share by id
    gui                 run gui

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   Your OwnCloud username
  --password PASSWORD   Your OwnCloud password
  --url URL             Your OwnCloud url, eg https://example.com/owncloud/
  ```

######Examples:
Get a list of shares

```./ocssharetools.py --user Bob --pass secret --url http://example.com/ownCloud getshares```

Create a public share link with a password

```./ocssharetools.py --user Bob --pass secret --url http://example.com/ownCloud create --path /NewDocument.odt --share-type=3 --share=password secret```

Create a share with a user

```./ocssharetools.py --user Bob --pass secret --url http://example.com/ownCloud create --path /NewDocument.odt --share-type=0 --share-with=Steve```

Create a share with a group

```./ocssharetools.py --user Bob --pass secret --url http://example.com/ownCloud create --path /NewDocument.odt --share-type=1 --share-with=Developers```

Delete a share (ID number is obtained from getshares command)

```./ocssharetools.py --user Bob --pass secret --url http://example.com/ownCloud delete 32```

Update a share a share (ID number is obtained from getshares command), setting an expiry date

```./ocssharetools.py --user Bob --pass secret --url http://example.com/ownCloud update 32 --expire-date "31-01-2015"```

## Using the library

```python
# First off, import the library
from ocsharetools import *

# Initialise the library with your url, username and password
ocs = OCShareAPI('http://example.com/ownCloud', 'Bob', 'secret')

# Create a share
share = ocs.create_share(path='/NewDocument.odt', share_type=3)

# Print share URL
print(share.url)

# Set the expiry date to tomorrow.
import datetime
date = datetime.date.today() + datetime.timedelta(days=1)

share.update(expire_date=date)

# Delete the share
share.delete()
