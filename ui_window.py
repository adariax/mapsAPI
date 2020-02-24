# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(450, 450)
        MainWindow.setMinimumSize(QtCore.QSize(450, 450))
        MainWindow.setMaximumSize(QtCore.QSize(450, 450))
        self.gridLayout = QtWidgets.QGridLayout(MainWindow)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.map_container = QtWidgets.QLabel(MainWindow)
        self.map_container.setMinimumSize(QtCore.QSize(450, 450))
        self.map_container.setMaximumSize(QtCore.QSize(450, 450))
        self.map_container.setObjectName("map_container")
        self.gridLayout.addWidget(self.map_container, 0, 0, 1, 1)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OurPerfectMap"))
        self.map_container.setText(_translate("MainWindow", "TextLabel"))
