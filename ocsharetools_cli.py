from ocsharetools import *
import argparse

def defaultPermissions(namespace):
    if namespace.share_type == 3:
        return 1
    else:
        return 31

class BitwiseAdd(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        value = getattr(namespace, self.dest)
        value = value if value is not None else defaultPermissions(namespace)
        setattr(namespace, self.dest, value | self.const)

class BitwiseSubtract(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        value = getattr(namespace, self.dest)
        value = value if value is not None else defaultPermissions(namespace)
        setattr(namespace, self.dest, value & ~self.const)


parser = argparse.ArgumentParser(description='Perform OCS Share API calls')
parser.add_argument('--username',
                    dest='username',
                    required=True,
                    help='Your OwnCloud username')
parser.add_argument('--password',
                    dest='password',
                    required=True,
                    help='Your OwnCloud password')
parser.add_argument('--url',
                    dest='url',
                    required=True,
                    help='Your OwnCloud url, eg https://example.com/owncloud/')



subparsers = parser.add_subparsers(help='Available commands', dest="subparser_name")
parser_get_shares = subparsers.add_parser('getshares', help='get Shares from a specific file or folder')
parser_get_shares.add_argument('--path', type=str, help='path to file/folder')
parser_get_shares.add_argument('--enable-reshares',
                               action='store_const',
                               const=True,
                               default=False,
                               help='returns not only the shares from the current user but all shares from the given file.')
parser_get_shares.add_argument('--enable-subfiles',
                               action='store_const',
                               const=True,
                               default=False,
                               help='returns all shares within a folder, given that path defines a folder')

parser_get_shares = subparsers.add_parser('getshare', help='get a single share by id')
parser_get_shares.add_argument('id', type=int, help='share id')

parser_get_shares = subparsers.add_parser('create', help='create a share')
parser_get_shares.add_argument('--path', type=str, required=True, help='path to the file/folder which should be shared')
parser_get_shares.add_argument('--share-type', type=int, required=True, help='who to share the file with 0 = user; 1 = group; 3 = public link')
parser_get_shares.add_argument('--share-with', type=str, help='user / group id with which the file should be shared')
parser_get_shares.add_argument('--public-upload',
                               action='store_const',
                               const=True,
                               default=False,
                               help='allow public upload to a public shared folder')
parser_get_shares.add_argument('--share-password', type=str, help='password to protect public link Share with')
parser_get_shares.add_argument('--allow-read',
                               action=BitwiseAdd,
                               nargs=0,
                               const=1,
                               dest='permissions',
                               help='give read access')
parser_get_shares.add_argument('--allow-update',
                               action=BitwiseAdd,
                               nargs=0,
                               const=2,
                               dest='permissions',
                               help='give update access')
parser_get_shares.add_argument('--allow-create',
                               action=BitwiseAdd,
                               nargs=0,
                               const=4,
                               dest='permissions',
                               help='give create access')
parser_get_shares.add_argument('--allow-delete',
                               action=BitwiseAdd,
                               nargs=0,
                               const=8,
                               dest='permissions',
                               help='give delete access')
parser_get_shares.add_argument('--allow-share',
                               action=BitwiseAdd,
                               nargs=0,
                               const=16,
                               dest='permissions',
                               help='give share access')
parser_get_shares.add_argument('--deny-read',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=1,
                               dest='permissions',
                               help='deny read access')
parser_get_shares.add_argument('--deny-update',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=2,
                               dest='permissions',
                               help='deny update access')
parser_get_shares.add_argument('--deny-create',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=4,
                               dest='permissions',
                               help='deny create access')
parser_get_shares.add_argument('--deny-delete',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=8,
                               dest='permissions',
                               help='deny delete access')
parser_get_shares.add_argument('--deny-share',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=16,
                               dest='permissions',
                               help='deny share access')

parser_get_shares = subparsers.add_parser('update', help='update a share')
parser_get_shares.add_argument('id', type=int, help='share id')
parser_get_shares.add_argument('--public-upload',
                               action='store_const',
                               const=True,
                               default=False,
                               help='allow public upload to a public shared folder')
parser_get_shares.add_argument('--share-password', type=str, help='password to protect public link Share with')
parser_get_shares.add_argument('--allow-read',
                               action=BitwiseAdd,
                               nargs=0,
                               const=1,
                               dest='permissions',
                               help='give read access')
parser_get_shares.add_argument('--allow-update',
                               action=BitwiseAdd,
                               nargs=0,
                               const=2,
                               dest='permissions',
                               help='give update access')
parser_get_shares.add_argument('--allow-create',
                               action=BitwiseAdd,
                               nargs=0,
                               const=4,
                               dest='permissions',
                               help='give create access')
parser_get_shares.add_argument('--allow-delete',
                               action=BitwiseAdd,
                               nargs=0,
                               const=8,
                               dest='permissions',
                               help='give delete access')
parser_get_shares.add_argument('--allow-share',
                               action=BitwiseAdd,
                               nargs=0,
                               const=16,
                               dest='permissions',
                               help='give share access')
parser_get_shares.add_argument('--deny-read',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=1,
                               dest='permissions',
                               help='deny read access')
parser_get_shares.add_argument('--deny-update',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=2,
                               dest='permissions',
                               help='deny update access')
parser_get_shares.add_argument('--deny-create',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=4,
                               dest='permissions',
                               help='deny create access')
parser_get_shares.add_argument('--deny-delete',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=8,
                               dest='permissions',
                               help='deny delete access')
parser_get_shares.add_argument('--deny-share',
                               action=BitwiseSubtract,
                               nargs=0,
                               const=16,
                               dest='permissions',
                               help='deny share access')

parser_get_shares = subparsers.add_parser('delete', help='delete a share by id')
parser_get_shares.add_argument('id', type=int, help='share id to delete')

parser_get_shares = subparsers.add_parser('gui', help='run gui')
parser_get_shares.add_argument('--path', type=str, required=True, help='path to the file/folder which should be shared')

args = parser.parse_args()
ocs = OCShareAPI(args.url, args.username, args.password)
if args.subparser_name == "gui":
    import ocsharetools_gui
    ocsharetools_gui.run(args)
try:
    if args.subparser_name == "getshares":
        shares = ocs.get_shares(path=args.path, reshares=args.enable_reshares, subfiles=args.enable_subfiles)
        for share in shares:
            print("#%d %s %s" % (share.id, share.url, share.path))
    elif args.subparser_name == "getshare":
        share = ocs.get_share_by_id(share_id=args.id)
        print("#%d %s %s" % (share.id, share.url, share.path))
    elif args.subparser_name == "create":
        share = ocs.create_share(path=args.path, shareType=args.share_type, shareWith=args.share_with,
                                 publicUpload=args.public_upload, password=args.share_password, permissions=args.permissions)
        print("#%d %s %s") % (share.id, share.url, share.path)
    elif args.subparser_name == "delete":
        ocs.delete_share_by_id(args.id)
    elif args.subparser_name == "update":
        ocs.update_share_by_id(share_id=args.id, permissions=args.permissions, password=args.share_password, publicUpload=args.public_upload)
except OCSShareException as e:
    print(e)
