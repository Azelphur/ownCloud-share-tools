import sys
import datetime
from PyQt5 import QtGui, QtCore, QtWidgets
import shutil
from ocsharetools import *


class OCShareTool(QtWidgets.QWidget):

    def __init__(self, args):
        super(OCShareTool, self).__init__()
        self.args = args
        if not os.path.exists(args.path):
            QtWidgets.QMessageBox.critical(
                self,
                'OC Share Tools',
                'File does not exist',
                QtWidgets.QMessageBox.Ok
            )
            sys.exit(0)

        self.ocs = OCShareAPI(args.url, args.username, args.password)
        self.public_share = None
        self.dialog_open = False
        self.cloud_path = full_path_to_cloud(args.path)
        if self.cloud_path is None:
            if args.instant_upload_path:
                path = args.instant_upload_path
            else:
                path = get_instant_upload_path()
            if not path or not os.path.exists(path):
                QtWidgets.QMessageBox.critical(
                    self,
                    'OC Share Tools',
                    'This file is not in an ownCloud share',
                    QtWidgets.QMessageBox.Ok
                )
                sys.exit(0)
            reply = QtWidgets.QMessageBox.question(
                self, 'ownCloud',
                'File is not in an ownCloud share directory. '
                'Move to instant uploads?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.Yes:
                self.cloud_path = full_path_to_cloud(
                    path+os.path.basename(args.path)
                )
                shutil.move(args.path, path)
            else:
                sys.exit(0)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )

        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addStretch(1)
        vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.groupEdit = QtWidgets.QLineEdit()
        self.groupEdit.setPlaceholderText('Share with group...')
        vbox.addWidget(self.groupEdit)

        self.userEdit = QtWidgets.QLineEdit()
        self.userEdit.setPlaceholderText('Share with user...')
        vbox.addWidget(self.userEdit)

        self.shareListVBox = QtWidgets.QVBoxLayout()
        vbox.addLayout(self.shareListVBox)

        horizontalLine = QtWidgets.QFrame()
        horizontalLine.setFrameStyle(QtWidgets.QFrame.HLine)
        horizontalLine.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        )
        vbox.addWidget(horizontalLine)

        self.shareCB = QtWidgets.QCheckBox('Share Link', self)
        vbox.addWidget(self.shareCB)

        self.shareHBox = QtWidgets.QHBoxLayout()
        self.copyButton = QtWidgets.QPushButton(
            QtGui.QIcon.fromTheme('edit-copy'),
            '',
            self
        )
        self.copyButton.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        self.shareEdit = QtWidgets.QLineEdit()
        self.shareHBox.addWidget(self.shareEdit)
        self.shareHBox.addWidget(self.copyButton)
        vbox.addLayout(self.shareHBox)

        self.passwordCB = QtWidgets.QCheckBox('Password Protect', self)
        vbox.addWidget(self.passwordCB)

        self.passwordEdit = QtWidgets.QLineEdit()
        self.passwordEdit.setPlaceholderText(
            'Choose a password for the public link'
        )
        self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        vbox.addWidget(self.passwordEdit)

        self.expirationCB = QtWidgets.QCheckBox(
            'Set expiration date',
            self
        )
        vbox.addWidget(self.expirationCB)

        self.calendar = QtWidgets.QCalendarWidget(self)
        vbox.addWidget(self.calendar)

        self.setLayout(vbox)

        self.setWindowTitle('OwnCloud Share')

        self.hide_share()
        self.get_shares()

        self.calendar.clicked[QtCore.QDate].connect(self.date_selected)
        self.groupEdit.returnPressed.connect(
            lambda: self.add_share(SHARETYPE_GROUP, self.groupEdit)
        )
        self.userEdit.returnPressed.connect(
            lambda: self.add_share(SHARETYPE_USER, self.userEdit)
        )
        self.passwordEdit.returnPressed.connect(self.set_password)
        self.passwordCB.stateChanged.connect(
            self.password_check_changed
        )
        self.shareCB.stateChanged.connect(self.share_link)
        self.copyButton.clicked.connect(self.copy_button_clicked)
        self.expirationCB.stateChanged.connect(
            self.expiration_check_changed
        )

        self.show()

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QtWidgets.QWidgetItem):
                item.widget().close()
            else:
                self.clear_layout(item.layout())
            layout.removeItem(item)

    def get_shares(self):
        self.shares = {}
        if self.cloud_path:
            try:
                shares = self.ocs.get_shares(path=self.cloud_path)
                for share in shares:
                    self.shares[share.id] = share
            except OCShareException:
                pass
        self.clear_layout(self.shareListVBox)
        for share_id, share in self.shares.items():
            if share.share_type == 3:
                self.shareCB.setChecked(True)
                self.shareEdit.setText(share.url)
                self.show_share()
                self.public_share = share
                if share.share_with is not None:
                    if self.passwordEdit.text() == '':
                        self.passwordEdit.setText('********')
                    self.passwordEdit.show()
                    self.passwordCB.setChecked(True)
                if share.expiration is not None:
                    self.expirationCB.setChecked(True)
                    self.calendar.show()
                    date = datetime.datetime.strptime(
                        share.expiration,
                        "%Y-%m-%d %H:%M:%S"
                    )
                    self.calendar.setSelectedDate(
                        QtCore.QDate(date.year, date.month, date.day)
                    )
            else:
                self.add_share_widgets(share)

    def add_share_widgets(self, share):
        if share.share_type == 1:
            title = '%s (group)' % (share.share_with)
        else:
            title = share.share_with
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(
            QtWidgets.QLabel(
                title,
                self
            )
        )
        canShare = QtWidgets.QCheckBox('can share', self)
        self.setup_share_tickbox(
            canShare,
            share,
            PERMISSION_SHARE
        )
        hbox.addWidget(canShare)
        canShare = QtWidgets.QCheckBox('can edit', self)
        self.setup_share_tickbox(
            canShare,
            share,
            PERMISSION_UPDATE
        )
        hbox.addWidget(canShare)
        deleteButton = QtWidgets.QPushButton(
            QtGui.QIcon.fromTheme('edit-delete'),
            '',
            self
        )
        deleteButton.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        deleteButton.clicked.connect(
            self.create_delete_button(hbox, share)
        )

        hbox.addWidget(deleteButton)
        self.shareListVBox.addLayout(hbox)

    def add_share(self, share_type, line_edit):
        try:
            share = self.ocs.create_share(
                path=self.cloud_path,
                share_type=share_type,
                share_with=line_edit.text()
            )
            self.shares[share.id] = share
            self.add_share_widgets(share)
        except OCShareException as e:
            self.dialog_open = True
            QtWidgets.QMessageBox.critical(
                self,
                'ownCloud Error %d' % (e.status_code),
                e.message,
                QtWidgets.QMessageBox.Ok
            )
            self.dialog_open = False
        line_edit.setText('')

    def date_selected(self, date):
        self.public_share.update(expire_date=date.toPyDate())

    def create_delete_button(self, hbox, share):
        return lambda checked: self.delete_clicked(
            checked,
            share,
            hbox
        )

    def delete_clicked(self, event, share, layout):
        del self.shares[share.id]
        share.delete()
        self.clear_layout(layout)
        self.shareListVBox.removeItem(layout)

    def setup_share_tickbox(self, checkbox, share, permission):
        if share.permissions & permission:
            checkbox.setChecked(True)
        checkbox.stateChanged.connect(
            lambda state: self.change_permission(
                state,
                share,
                permission
            )
        )

    def hide_share(self):
        self.shareEdit.hide()
        self.copyButton.hide()
        self.passwordCB.hide()
        self.passwordCB.setChecked(False)
        self.passwordEdit.hide()
        self.expirationCB.hide()
        self.expirationCB.setChecked(False)
        self.calendar.hide()

    def show_share(self):
        self.shareEdit.show()
        self.copyButton.show()
        self.passwordCB.show()
        self.expirationCB.show()

    def change_permission(self, checked, share, permission):
        if checked == QtCore.Qt.Checked:
            share.update(permissions=share.permissions | permission)
        else:
            share.update(permissions=share.permissions & ~permission)

    def set_password(self):
        self.public_share.update(password=self.passwordEdit.text())
        self.passwordEdit.setPlaceholderText('Password Set')
        self.get_shares()
        self.passwordEdit.setText('')

    def copy_button_clicked(self, event):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.public_share.url)

    def password_check_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.passwordEdit.show()
        else:
            self.public_share.update(password=False)
            self.get_shares()
            self.passwordEdit.setText('')
            self.passwordEdit.setPlaceholderText(
                'Choose a password for the public link'
            )
            self.passwordEdit.hide()

    def expiration_check_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.calendar.show()
            date = datetime.date.today() + datetime.timedelta(days=1)
            self.public_share.update(
                expire_date=date
            )
            date = QtCore.QDate(date.year, date.month, date.day)
            self.calendar.setSelectedDate(date)
        elif self.public_share:
            self.public_share.update(expire_date=False)
            self.calendar.hide()

    def share_link(self, state):
        if state == QtCore.Qt.Checked:
            share = self.ocs.create_share(
                path=self.cloud_path,
                share_type=SHARETYPE_PUBLIC
            )
            self.shares[share.id] = share
            self.public_share = share
            self.shareEdit.setText(self.public_share.url)
            self.show_share()
        else:
            del self.shares[self.public_share.id]
            self.public_share.delete()
            self.public_share = None
            self.hide_share()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def focus_changed(self, old, now):
        if (now is None and
                QtWidgets.QApplication.activeWindow() is None and
                self.dialog_open is False):
            self.close()


def run(args):
    app = QtWidgets.QApplication(sys.argv)
    ex = OCShareTool(args)
    app.focusChanged.connect(ex.focus_changed)
    e = app.exec_()
    clipboard = QtWidgets.QApplication.clipboard()
    event = QtCore.QEvent(QtCore.QEvent.Clipboard)
    QtWidgets.QApplication.sendEvent(clipboard, event)
    sys.exit(e)
