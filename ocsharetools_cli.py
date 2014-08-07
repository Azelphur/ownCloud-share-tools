from ocsharetools import *
import argparse
from datetime import datetime


def defaultPermissions(share_type):
    if share_type == 3:
        return 1
    else:
        return 31


def calcPermissions(allow, deny, default):
    if allow:
        for i in allow:
            default = default | i
    if deny:
        for i in deny:
            default = default & ~i
    return default


def add_permission_flags(parser):
    parser.add_argument(
        '--allow-read',
        action='append_const',
        const=1,
        dest='permissions_allow',
        help='give read access'
    )
    parser.add_argument(
        '--allow-update',
        action='append_const',
        const=2,
        dest='permissions_allow',
        help='give update access'
    )
    parser.add_argument(
        '--allow-create',
        action='append_const',
        const=4,
        dest='permissions_allow',
        help='give create access'
    )
    parser.add_argument(
        '--allow-delete',
        action='append_const',
        const=8,
        dest='permissions_allow',
        help='give delete access'
    )
    parser.add_argument(
        '--allow-share',
        action='append_const',
        const=16,
        dest='permissions_allow',
        help='give share access'
    )
    parser.add_argument(
        '--deny-read',
        action='append_const',
        const=1,
        dest='permissions_deny',
        help='deny read access'
    )
    parser.add_argument(
        '--deny-update',
        action='append_const',
        const=2,
        dest='permissions_deny',
        help='deny update access'
    )
    parser.add_argument(
        '--deny-create',
        action='append_const',
        const=4,
        dest='permissions_deny',
        help='deny create access'
    )
    parser.add_argument(
        '--deny-delete',
        action='append_const',
        const=8,
        dest='permissions',
        help='deny delete access'
    )
    parser.add_argument(
        '--deny-share',
        action='append_const',
        const=16,
        dest='permissions_deny',
        help='deny share access'
    )


def run():
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
                        help='Your OwnCloud url, eg '
                             'https://example.com/owncloud/')

    subparsers = parser.add_subparsers(
        help='Available commands',
        dest="subparser_name"
    )
    parser_get_shares = subparsers.add_parser(
        'getshares',
        help='get Shares from a specific file or folder'
    )
    parser_get_shares.add_argument(
        '--path',
        type=str,
        help='path to file/folder'
    )
    parser_get_shares.add_argument(
        '--enable-reshares',
        action='store_const',
        const=True,
        default=False,
        help='returns not only the shares from the current '
             'user but all shares from the given file.'
    )
    parser_get_shares.add_argument(
        '--enable-subfiles',
        action='store_const',
        const=True,
        default=False,
        help='returns all shares within a folder, '
             'given that path defines a folder'
    )

    parser_get_share = subparsers.add_parser(
        'getshare',
        help='get a single share by id'
    )
    parser_get_share.add_argument('id', type=int, help='share id')

    parser_create = subparsers.add_parser('create', help='create a share')
    parser_create.add_argument(
        '--path',
        type=str,
        required=True,
        help='path to the file/folder which should be shared'
    )
    parser_create.add_argument(
        '--share-type',
        type=int,
        required=True,
        help='who to share the file with 0 = user; 1 = group; 3 = public link'
    )
    parser_create.add_argument(
        '--share-with',
        type=str,
        help='user / group id with which the file should be shared'
    )
    parser_create.add_argument(
        '--public-upload',
        action='store_const',
        const=True,
        default=False,
        help='allow public upload to a public shared folder'
    )
    parser_create.add_argument(
        '--share-password',
        type=str,
        help='password to protect public link Share with'
    )
    add_permission_flags(parser_create)

    parser_update = subparsers.add_parser('update', help='update a share')
    parser_update.add_argument('id', type=int, help='share id')
    parser_update.add_argument(
        '--public-upload',
        action='store_const',
        const=True,
        default=None,
        help='allow public upload to a public shared folder'
    )
    parser_update.add_argument(
        '--share-password',
        type=str,
        help='password to protect public link Share with'
    )
    parser_update.add_argument(
        '--expire-date',
        type=str,
        help='Expiry date, in DD-MM-YYYY format'
    )
    parser_update.add_argument(
        '--disable-expire-date',
        action='store_const',
        const=True,
        default=False,
        help='Disable the expiry date'
    )
    add_permission_flags(parser_update)

    parser_delete = subparsers.add_parser(
        'delete',
        help='delete a share by id'
    )
    parser_delete.add_argument('id', type=int, help='share id to delete')

    parser_delete = subparsers.add_parser('gui', help='run gui')
    parser_delete.add_argument(
        '--path',
        type=str,
        required=True,
        help='path to the file/folder which should be shared'
    )
    parser_delete.add_argument(
        '--instant-upload-path',
        type=str,
        required=False,
        help='path to do instant uploads to, if required'
    )

    args = parser.parse_args()
    ocs = OCShareAPI(args.url, args.username, args.password)
    if args.subparser_name == "gui":
        import ocsharetools_gui
        ocsharetools_gui.run(args)
    try:
        if args.subparser_name == "getshares":
            shares = ocs.get_shares(
                path=args.path,
                reshares=args.enable_reshares,
                subfiles=args.enable_subfiles
            )
            for share in shares:
                print("#%d %s %s" % (share.id, share.url, share.path))
        elif args.subparser_name == "getshare":
            share = ocs.get_share_by_id(share_id=args.id)
            print("#%d %s %s" % (share.id, share.url, share.path))
        elif args.subparser_name == "create":
            share = ocs.create_share(
                path=args.path,
                shareType=args.share_type,
                shareWith=args.share_with,
                publicUpload=args.public_upload,
                password=args.share_password,
                permissions=calcPermissions(
                    args.permissions_allow,
                    args.permissions_deny,
                    defaultPermissions(args.share_type)
                )
            )
            print("#%d %s %s" % (share.id, share.url, share.path))
        elif args.subparser_name == "delete":
            ocs.delete_share_by_id(args.id)
        elif args.subparser_name == "update":
            if args.permissions_allow or args.permissions_deny:
                share = ocs.get_share_by_id(args.id)
                permissions = calcPermissions(
                    args.permissions_allow,
                    args.permissions_deny,
                    share.permissions
                )
            else:
                permissions = None

            if args.disable_expire_date:
                expire_date = False
            elif args.expire_date:
                expire_date = datetime.strptime(args.expire_date, "%d-%m-%Y")
            else:
                expire_date = None

            ocs.update_share_by_id(
                share_id=args.id,
                permissions=permissions,
                password=args.share_password,
                publicUpload=args.public_upload,
                expireDate=expire_date
            )
    except OCShareException as e:
        print(e)
