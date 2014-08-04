import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from ocsharetools import *

class OCShareTool(QtWidgets.QWidget):

    def __init__(self, args):
        super(OCShareTool, self).__init__()
        self.args = args
        self.ocs = OCShareAPI(args.url, args.username, args.password)
        self.cloudPath = full_path_to_cloud(args.path)
        self.public_share = None
        if self.cloudPath:
            try:
                self.shares = self.ocs.get_shares(path=self.cloudPath)
            except OCShareException:
                self.shares = []
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

        groupEdit = QtWidgets.QLineEdit()
        groupEdit.setFixedWidth(300)
        groupEdit.setPlaceholderText('Share with user or group...')
        vbox.addWidget(groupEdit)

        self.shareListVBox = QtWidgets.QVBoxLayout()
        self.shareListHBoxes = []
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
        self.copyButton.resize(self.copyButton.sizeHint())

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
        self.calendar.setSelectedDate(QtCore.QDate())
        self.calendar.clicked[QtCore.QDate].connect(self.date_selected)
        vbox.addWidget(self.calendar)

        self.setLayout(vbox)

        self.setWindowTitle('OwnCloud Share')

        self.hide_share()
        for share in self.shares:
            if share.share_type == 3:
                self.shareCB.setChecked(True)
                self.shareEdit.setText(share.url)
                self.show_share()
                self.public_share = share
                if share.share_with is not None:
                    self.passwordEdit.setText('********')
                    self.passwordEdit.show()
                    self.passwordCB.setChecked(True)
                if share.expiration is not None:
                    pass
            else:
                if share.share_type == 1:
                    title = '%s (group)' % (share.share_with)
                else:
                    title = share.share_with
                hbox = QtWidgets.QHBoxLayout()
                self.shareListHBoxes += [hbox]
                hbox.addWidget(
                    QtWidgets.QLabel(
                        title,
                        self
                    )
                )
                canShare = QtWidgets.QCheckBox('can share', self)
                self.setupShareTickbox(
                    canShare,
                    share,
                    PERMISSION_SHARE
                )
                hbox.addWidget(canShare)
                canShare = QtWidgets.QCheckBox('can edit', self)
                self.setupShareTickbox(
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
                deleteButton.clicked.connect(
                    self.create_delete_button(hbox, share)
                )

                hbox.addWidget(deleteButton)
                self.shareListVBox.addLayout(hbox)

        self.passwordEdit.textChanged.connect(self.password_changed)
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

    def date_selected(self, date):
        print(date.toPyDate().ctime())

    def create_delete_button(self, hbox, share):
        return lambda checked: self.delete_clicked(
            checked,
            share,
            hbox
        )

    def delete_clicked(self, event, share, layout):
        for i in range(0, len(self.shares)):
            if self.shares[i] == share:
                del self.shares[i]
                break
        share.delete()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            item.widget().close()
            layout.removeItem(item)

    def setupShareTickbox(self, checkbox, share, permission):
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

    def password_changed(self):
        self.passwordEdit.setPlaceholderText(
            'Choose a password for the public link'
        )

    def set_password(self):
        self.public_share.update(password=self.passwordEdit.text())
        self.shares = self.ocs.get_shares(path=self.cloudPath)
        self.passwordEdit.setText('')
        self.passwordEdit.setPlaceholderText('Password Set')

    def copy_button_clicked(self, event):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.public_share.url)

    def password_check_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.passwordEdit.show()
        else:
            self.passwordEdit.hide()

    def expiration_check_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.calendar.show()
        else:
            self.calendar.hide()

    def share_link(self, state):
        if state == QtCore.Qt.Checked:
            self.share = self.ocs.create_share(
                path=self.cloudPath,
                shareType=SHARETYPE_PUBLIC
            )
            self.shareEdit.setText(self.share.url)
            self.show_share()
        else:
            self.ocs.delete_share(share=self.public_share)
            self.hide_share()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def focus_changed(self, old, now):
        if (now is None and
                QtWidgets.QApplication.activeWindow() is None):
            return
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
