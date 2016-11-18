# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import os
from PyQt4 import QtGui, QtCore
from testerwidget import TesterWidget
from testselector import TestSelector
from settingswindow import SettingsWindow

class TesterPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.lastSettings = {}
        self.widget = None
        self.iface.initializationCompleted.connect(self.hideWidget)

    def hideWidget(self):
        if self.widget:
            self.widget.hide()

    def unload(self):
        self.iface.removePluginMenu(u"Tester", self.action)
        del self.action
        if self.widget:
            self.widget.hide()
            del self.widget

    def initGui(self):
        self.action = QtGui.QAction("Start testing", self.iface.mainWindow())
        self.action.triggered.connect(self.test)
        self.iface.addPluginToMenu(u"Tester", self.action)

    def test(self):
        if self.widget is not None and self.widget.isVisible():
            QtGui.QMessageBox.warning(self.iface.mainWindow(), "Tester plugin", "A test cycle is currently being run")
            return
        dlg = TestSelector()
        dlg.exec_()
        if dlg.tests:
            settings = {}
            for test in dlg.tests:
                settings.update(test.settings)
            settings.update(self.lastSettings)
            if settings:
                settingsDlg = SettingsWindow(settings)
                settingsDlg.exec_()
                if not settingsDlg.settings:
                    return
                self.lastSettings = settingsDlg.settings
                for key, value in settingsDlg.settings.iteritems():
                    os.environ[key] = value
            self.widget = TesterWidget()
            self.widget.testingFinished.connect(self.testingFinished)
            self.iface.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.widget)
            self.widget.show()
            self.widget.setTests(dlg.tests)
            self.widget.startTesting()

    def testingFinished(self):
        dlg = self.widget.getReportDialog()
        dlg.exec_()
        reopen = dlg.reopen
        self.widget = None
        if reopen:
            self.test()


