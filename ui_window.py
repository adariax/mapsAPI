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
        MainWindow.resize(450, 600)
        MainWindow.setMinimumSize(QtCore.QSize(450, 600))
        MainWindow.setMaximumSize(QtCore.QSize(450, 600))
        self.gridLayout = QtWidgets.QGridLayout(MainWindow)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.map_container = QtWidgets.QLabel(MainWindow)
        self.map_container.setMinimumSize(QtCore.QSize(450, 450))
        self.map_container.setMaximumSize(QtCore.QSize(450, 450))
        self.map_container.setObjectName("map_container")
        self.gridLayout.addWidget(self.map_container, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(11)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cb_trf = QtWidgets.QCheckBox(MainWindow)
        self.cb_trf.setObjectName("cb_trf")
        self.verticalLayout.addWidget(self.cb_trf)
        self.cb_skl = QtWidgets.QCheckBox(MainWindow)
        self.cb_skl.setObjectName("cb_skl")
        self.verticalLayout.addWidget(self.cb_skl)
        self.rb_sat = QtWidgets.QRadioButton(MainWindow)
        self.rb_sat.setObjectName("rb_sat")
        self.verticalLayout.addWidget(self.rb_sat)
        self.rb_map = QtWidgets.QRadioButton(MainWindow)
        self.rb_map.setChecked(True)
        self.rb_map.setObjectName("rb_map")
        self.verticalLayout.addWidget(self.rb_map)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OurPerfectMap"))
        self.map_container.setText(_translate("MainWindow", "TextLabel"))
        self.cb_trf.setAccessibleName(_translate("MainWindow", "trf"))
        self.cb_trf.setText(_translate("MainWindow", "Пробки"))
        self.cb_skl.setAccessibleName(_translate("MainWindow", "skl"))
        self.cb_skl.setText(_translate("MainWindow", "Название объкетов"))
        self.rb_sat.setAccessibleName(_translate("MainWindow", "sat"))
        self.rb_sat.setText(_translate("MainWindow", "Спутник"))
        self.rb_map.setAccessibleName(_translate("MainWindow", "map"))
        self.rb_map.setText(_translate("MainWindow", "Схема"))
