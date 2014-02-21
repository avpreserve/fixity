# Fixity GUI
# Version 0.3, 2013-10-28
# Copyright (c) 2013 AudioVisual Preservation Solutions
# All rights reserved.
# Released under the Apache license, v. 2.0

#Bultin Libraries
from PySide.QtCore import *
from PySide.QtGui import *
from os import path, listdir, remove, walk , getcwd , P_DETACH , spawnl , system
import re
import datetime
import shutil
import sys
import platform
import os
from collections import deque
from genericpath import exists

#Custom Libraries
import FixityCore
import FixitySchtask
from Threading import Threading
from EmailPref import EmailPref
from Debuger import Debuger
from FilterFiles import FilterFiles
from FileChanged import FileChanged
from DecryptionManager import DecryptionManager



class ProjectWin(QMainWindow):
        def __init__(self, EmailPref , FilterFiles):
                
                QMainWindow.__init__(self)
                Debuggin = Debuger()
                Debuggin.tureDebugerOn()
                Debuggin.logInfo('Logger started!::::::::::::::::::' + "\n" ,{} )
                
                
                self.SystemInformation = self.getWindowsInformation()
                if(self.SystemInformation):
                    Debuggin.logInfo('System Information' + "\n" ,{})
                    Debuggin.logInfo('platform = '+str(self.SystemInformation['platform'])  , {} )
                    Debuggin.logInfo('major = '+ str(self.SystemInformation['major']) , {} )
                    Debuggin.logInfo('minor = '+str(self.SystemInformation['minor'])  , {} )
                    Debuggin.logInfo('build = '+str(self.SystemInformation['build'])  , {} )
                    Debuggin.logInfo('platformType = '+str(self.SystemInformation['platformType'])  , {} )
                    Debuggin.logInfo('isWindows = '+str(self.SystemInformation['isWindows'])  , {} )
                    Debuggin.logInfo('WindowsType = '+str(self.SystemInformation['WindowsType'])  , {} )
                    Debuggin.logInfo('bitType = '+str(self.SystemInformation['bitType'])  , {} )
                
                self.EP = EmailPref()
                self.EP.setVersion('0.3')
                self.DecryptionManager = DecryptionManager()
                self.FileChanged = FileChanged()
                self.FileChanged.setVersion('0.3')
                
                self.FilterFiles = FilterFiles()
                self.Threading = Threading
                if not path.isfile(getcwd() + '\\bin\\conf.txt'):
                    fileConf = open(getcwd() + '\\bin\\conf.txt', 'w+')
                    fileConf.close()
                    
                self.setWindowIcon(QIcon(path.join(getcwd(), 'images\\logo_sign_small.png')))
                versoin = self.EP.getVersion()
                self.setWindowTitle("Fixity "+versoin);
                self.unsaved = False
                menubar = self.menuBar()
                self.f = menubar.addMenu('&File')
                self.Preferences = menubar.addMenu('&Preferences')
                newp = QAction('&New Project', self)
                
                save = QAction('&Run Now', self)
                usch = QAction('&Save Settings', self)
                dlte = QAction('&Delete Project', self)
                configemail = QAction('&Configure Sender Email', self)
                quit = QAction('&Quit Fixity', self)
                
                FilterFilesMane = QAction('&Filter Files', self)
                DecryptionManagerMenu = QAction('&Select Checksum Algorithm', self)
                
                self.Debuging = QAction('&Turn Debugging Off', self)
                self.switchDebugger('start')
             
                    
                self.f.addAction(newp)
                self.f.addAction(usch)
                self.f.addAction(save)
                self.f.addAction(dlte)
                self.f.addAction(quit)
                
                self.Preferences.addAction(FilterFilesMane)
                self.Preferences.addAction(configemail)
                self.Preferences.addAction(self.Debuging)
                self.Preferences.addAction(DecryptionManagerMenu)
                
                dlte.triggered.connect(self.deleteproject)
                newp.triggered.connect(self.new)
                configemail.triggered.connect(self.ConfigEmailView)
                save.triggered.connect(self.run)
                usch.triggered.connect(self.updateschedule)
                quit.triggered.connect(self.close)
                
                FilterFilesMane.triggered.connect(self.FilterFilesBox)
                DecryptionManagerMenu.triggered.connect(self.DecryptionManagerBox)
                self.Debuging.triggered.connect(self.switchDebugger)
                
                self.widget = QWidget(self)
                
                self.pgroup = QGroupBox("Projects")
                self.play = QVBoxLayout()
                self.projects = QListWidget(self)
                
                self.projects.setFixedSize(115, 190)

                for p in listdir('projects\\'):
                    if not '.tmp.' in p:
                        QListWidgetItem(p.replace('.fxy', ''), self.projects)
                                
                self.play.addWidget(self.projects)
                self.pgroup.setLayout(self.play)
                
                self.sch = QGroupBox("Scheduling")
                self.monthly = QRadioButton("Monthly")
                self.weekly = QRadioButton("Weekly")
                self.daily = QRadioButton("Daily")
                
                self.runOnlyOnACPower = QCheckBox("Run when on battery power")
                self.StartWhenAvailable = QCheckBox("If missed, run upon restart")
                self.EmailOnlyWhenSomethingChanged = QCheckBox("Email only upon warning or failure")

                self.runOnlyOnACPower.setChecked(True)
                self.StartWhenAvailable.setChecked(True)
                self.EmailOnlyWhenSomethingChanged.setChecked(True)
                
                self.monthly.clicked.connect(self.monthclick)
                self.weekly.clicked.connect(self.weekclick)
                self.daily.clicked.connect(self.dayclick)
                
                slay = QVBoxLayout()
                
                slay.addWidget(self.monthly)
                slay.addWidget(self.weekly)
                slay.addWidget(self.daily)
                
                self.timer = QTimeEdit(QTime())
                self.timer.setDisplayFormat("HH:mm")    
                slay.addWidget(self.timer)
                
                self.dow = QComboBox()
                self.dow.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                self.dow.activated.connect(self.changed)
                slay.addWidget(self.dow)
                self.dow.hide()
                
                self.dom = QSpinBox()
                self.dom.setMaximum(31)
                self.dom.setMinimum(1)
                self.dom.valueChanged.connect(self.changed)
                slay.addWidget(self.dom)
                self.dom.hide()
                
                self.spacer = QSpacerItem(125, 30)
                slay.addItem(self.spacer)
                
                slay.addWidget(self.runOnlyOnACPower)
                slay.addWidget(self.StartWhenAvailable)
                slay.addWidget(self.EmailOnlyWhenSomethingChanged)

                
                self.lastrun = QLabel("Last checked: ")
                slay.addWidget(self.lastrun)
                self.sch.setLayout(slay)
                self.sch.setFixedSize(255, 269)
                
                self.mlay = QVBoxLayout()
                self.mlay.setSpacing(0)
                self.mtx = []
                for n in xrange(0, 7):
                        self.mtx.append(QLineEdit())
                        self.mlay.addWidget(self.mtx[n])
                        self.mtx[n].textChanged.connect(self.changed)
                
                self.dlay = QVBoxLayout()
                self.dlay.setSpacing(0)
                self.dtx, self.but = [], []
                
                for n in xrange(0, 7):
                        
                        hbox = QHBoxLayout()
                        hbox.setContentsMargins(0, 0, 0, 0)
                        hbox.setSpacing(0)
                        self.dtx.append(QLineEdit())
                        self.but.append(QPushButton('...'))
                        self.but[n].setFixedSize(30, 20)
                        self.but[n].clicked.connect(self.pickdir)
                        self.dtx[n].textChanged.connect(self.changed)
                        hbox.addWidget(self.dtx[n])
                        hbox.addWidget(self.but[n])
                        self.dlay.addLayout(hbox)
                
                self.dirs = QGroupBox("Directories")
                self.mail = QGroupBox("Recipient Email Addresses")
                self.dirs.setLayout(self.dlay)
                self.mail.setLayout(self.mlay)
                
                self.main = QHBoxLayout()
                
                self.main.addWidget(self.pgroup)
                self.main.addWidget(self.sch)
                self.main.addWidget(self.dirs)
                self.main.addWidget(self.mail) 
                
                self.widget.setLayout(self.main)
                self.setCentralWidget(self.widget)
                self.projects.itemClicked.connect(self.update)
                if(self.SystemInformation and str(self.SystemInformation['WindowsType']) == '7'):
                    self.runOnlyOnACPower.setDisabled(False)
                    self.StartWhenAvailable.setDisabled(False)
                    self.EmailOnlyWhenSomethingChanged.setDisabled(False)
                    
                else:
                    
                    self.runOnlyOnACPower.setDisabled(True)
                    self.StartWhenAvailable.setDisabled(True)
                    self.EmailOnlyWhenSomethingChanged.setDisabled(True)
                    
                try:
                        self.old = self.projects.itemAt(0, 0)
                        self.update(self.old)
                        self.old.setSelected(True)
                except:

                        pass
                self.unsaved = False
                self.toggler((self.projects.count() == 0))
                self.show()
                       
        # Configure Email Address for the Tools
        def ConfigEmailView(self):
            self.EP.CloseClick()
            self.EP = None
            self.EP = EmailPref()
            self.EP.SetDesgin()
            self.EP.ShowDialog()
        
        # Pop Up to Change Root Directory If any change occured
        # orignalPathText:: Path In Manifest
        # changePathText:: New Path Given in Fixity Tool  
        def ChangeRootDirectoryInfor(self,orignalPathText,changePathText):
            self.FileChanged.DestroyEveryThing()
            self.FileChanged = None
            self.FileChanged = FileChanged(orignalPathText,changePathText)
            self.FileChanged.SetDesgin()
            self.FileChanged.ShowDialog()
            
        # Pop up to set Filters        
        def FilterFilesBox(self):
            self.FilterFiles.Cancel()
            self.FilterFiles = None
            self.FilterFiles = FilterFiles()
            self.FilterFiles.SetDesgin()
            self.FilterFiles.ShowDialog()    
            
        # Pop up to set Filters        
        def DecryptionManagerBox(self):
            self.DecryptionManager.Cancel()
            self.DecryptionManager = None
            self.DecryptionManager = DecryptionManager()
            self.DecryptionManager.SetDesgin()
            self.DecryptionManager.ShowDialog()
               
        def switchDebugger(self,start= None):
            
            Information = self.EP.getConfigInfo()            
            debugText = ''
            
            if start == None:
                if Information['debugging'] == 'debug|off' or Information['debugging'] == '' or Information['debugging'] == None:
                    Information['debugging'] ='debug|on'
                else:
                    Information['debugging'] ='debug|off'
            
            self.EP.setConfigInfo(Information)
            
            if Information['debugging'] == 'debug|off' or Information['debugging'] == '' or Information['debugging'] == None:
                debugText = 'Turn Debugging On' 
            else:
                debugText = 'Turn Debugging Off'
            
            self.Debuging.setText(debugText)    
            
        def newWindow(self):
            self = ProjectWin()
            self.show()
            sys.exit(app.exec_())
        def getWindowsInformation(self):
            WindowsInformation = {};
            try:
                major , minor , build , platformType , servicePack = sys.getwindowsversion()
                WindowsInformation['major'] = major
                WindowsInformation['minor'] = minor
                WindowsInformation['build'] = build 
                WindowsInformation['platformType'] = platformType
                WindowsInformation['servicePack'] = servicePack
                windowDetailedName = platform.platform()
                WindowsInformation['platform'] = windowDetailedName
                windowDetailedName = str(windowDetailedName).split('-')
                
                if(windowDetailedName[0] != None and (str(windowDetailedName[0]) == 'Windows' or str(windowDetailedName[0]) == 'windows')):  
                    WindowsInformation['isWindows'] =True
                else:
                    WindowsInformation['isWindows'] =False
                    
                if(windowDetailedName[1] != None and (str(windowDetailedName[1]) != '')):  
                    WindowsInformation['WindowsType'] =str(windowDetailedName[1])
                else:
                    WindowsInformation['WindowsType'] =None
                 
                WindowsInformation['ProcessorInfo'] = platform.processor()
                
                try:
                    os.environ["PROGRAMFILES(X86)"]
                    bits = 64
                except:
                    bits = 32
                    
                WindowsInformation['bitType'] = "Win{0}".format(bits)
            except Exception as e:
                Debuging = Debuger()
                moreInformation = {"moreInfo":'null'}
                try:
                    if not e[0] == None:
                        moreInformation['LogsMore'] =str(e[0])
                except:
                    pass
                try:    
                    if not e[1] == None:
                        moreInformation['LogsMore1'] =str(e[1])
                except:
                    pass
                    
                Debuging.tureDebugerOn()    
                Debuging.logError('Could Not get Windows Information Line range 220 - 240 File Fixity ', moreInformation)
                pass
            return WindowsInformation
            
        #Updates Fields When Project Is Selected In List
        @Slot(str)
        def update(self, new):
                if self.unsaved:
                        sbox = QMessageBox()
                        sbox.setText("There are unsaved changes to this project.")
                        sbox.setInformativeText("These will be discarded when opening a new project.\nWould you like to stay on this project?")
                        sbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Discard)
                        sbox.setDefaultButton(QMessageBox.Ok)
                        sval = sbox.exec_()
                        if sval == QMessageBox.Ok:
                                self.projects.setCurrentRow(self.projects.indexFromItem(self.old).row())
                                return
                projectName = self.old.text()           
                if not path.isfile('projects\\' + self.old.text() + '.fxy'):
                        projectName = self.old.text()
                        self.projects.takeItem(self.projects.row(self.old))
                try:
                        f = open('projects\\' + new.text() + '.fxy', 'rb')
                        projectName = new.text()
                except:
                        for n in xrange(0, 7):
                                self.dtx[n].setText("")
                                self.mtx[n].setText("")
                        self.timer.setTime(QTime(0, 0))
                        self.monthclick()
                        self.monthly.setChecked(True)
                        self.dom.setValue(1)
                        return
 
                information = {}
                 
                onlyonchange = self.EP.getConfigInfo(projectName)
                
                information['onlyonchange'] = onlyonchange['onlyonchange'].replace('EOWSC|', '').replace('\n', '')
                information['RunWhenOnBatteryPower'] = onlyonchange['RunWhenOnBatteryPower'].replace('RWOBP|', '').replace('\n', '')
                information['IfMissedRunUponAvailable'] = onlyonchange['IfMissedRunUponAvailable'].replace('IMRUA|', '').replace('\n', '')
                information['RunInitialScan'] = onlyonchange['RunInitialScan'].replace('RIS|', '').replace('\n', '')
                
                dlabel = f.readline()
                elabel = f.readline()
                slabel = f.readline()
                rlabel = f.readline()
                
                f.close()
                
                ds = dlabel.split(';')
                ms = elabel.split(';')
                
                n, p = 0, 0
                for n in xrange(0, 7):
                        try:
                                usages = str(ds[n]).split('|-|-|')
                                self.dtx[n].setText(usages[0].strip())
                        except:
                                self.dtx[n].setText("")
                        try:
                                self.mtx[n].setText(ms[n].strip())
                        except:
                                self.mtx[n].setText("")
                if information['onlyonchange'] == 'T':
                    self.EmailOnlyWhenSomethingChanged.setChecked(False)
                elif information['onlyonchange'] == 'F':
                    self.EmailOnlyWhenSomethingChanged.setChecked(True)
#       
                if information['RunWhenOnBatteryPower'] == 'T':
                    self.runOnlyOnACPower.setChecked(True)
                elif information['RunWhenOnBatteryPower'] == 'F':
                    self.runOnlyOnACPower.setChecked(False)
                 
                if information['IfMissedRunUponAvailable'] == 'T':
                    self.StartWhenAvailable.setChecked(True)
                elif information['IfMissedRunUponAvailable'] == 'F':
                    self.StartWhenAvailable.setChecked(False)

                sc = slabel.rstrip().split(' ')
                if sc[0] == '1':
                        self.monthly.setChecked(True)
                        self.monthclick()
                        self.dom.setValue(int(sc[2]))
                elif sc[0] == '2':
                        self.weekly.setChecked(True)
                        self.weekclick()
                        self.dow.setCurrentIndex(int(sc[3]))
                elif sc[0] == '3':
                        self.daily.setChecked(True)
                        self.dayclick()
                try:
                        t = sc[1].split(':')
                except:
                        t = ['00', '00']
                self.timer.setTime(QTime(int(t[0]), int(t[1])))
                self.lastrun.setText("Last checked:\n" + rlabel)
                self.unsaved = False
                self.old = new
                
                
        # New Project Creation
        def new(self):
                name = QInputDialog.getText(self, "Project Name", "Name for new Fixity project:", text="New_Project")
                if name[0] == "" or path.isfile("projects\\" + name[0] + ".fxy") or any(c in '\ <>:\"\/\\\|?*' for c in name[0]) or name[0][-1] == '.':
                        QMessageBox.warning(self, "Fixity", "Invalid project name:\n*Project names must be unique\n*Project names cannot be blank\n*Project names cannot contain spaces\n*Project names must be legal filenames")
                        return
                if not path.isfile(getcwd() + '\\bin\\' + name[0] + '-conf.txt'):
                    fileConf = open(getcwd() + '\\bin\\' + name[0] + '-conf.txt', 'w+')
                    fileConf.close() 
                if not path.isfile(getcwd() + '\\projects\\' + name[0] + '.fxy'):
                    fileConf = open(getcwd() + '\\projects\\' + name[0] + '.fxy', 'w+')
                    fileConf.close()         
                                       
                newitem = QListWidgetItem(name[0], self.projects)
                self.projects.setCurrentItem(newitem)
                self.monthly.setChecked(True)
                self.monthclick()
                self.dom.setValue(1)
                self.timer.setTime(QTime(0, 0))
                for x in xrange(0, 7):
                        self.dtx[x].setText("")
                        self.mtx[x].setText("")
                
                self.old = newitem
                self.toggler(False)
        def process(self, shouldRun=True):
                
                if all(d.text() == "" for d in self.dtx):
                        QMessageBox.warning(self, "Fixity", "No directories selected!\nPlease set directories to scan")
                        return
                dmonth, dweek = 99, 99
                if self.monthly.isChecked():
                        interval = 1
                        dmonth = int(self.dom.value())
                elif self.weekly.isChecked():
                        interval = 2
                        dweek = int(self.dow.currentIndex())
                elif self.daily.isChecked():
                        interval = 3
                else:
                        QMessageBox.warning(self, "Fixity", "Project schedule not set - please select an interval for scans")
                        return
                    
                for ms in self.mtx:
                        SingleEmail = ms.text().strip()
                        if  SingleEmail != "":
                            errorMsg = self.EP.ValidateEmail(SingleEmail)
                            if not str(errorMsg).strip() == 'None':
                                QB = QMessageBox()
                                errorMsg = QB.information(self, "Error", errorMsg)
                                return
                
                isfileExists = False    
                if path.isfile('projects\\' + self.projects.currentItem().text() + '.fxy'):
                    isfileExists = True
                    
                if isfileExists:
                    projFile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'rb')
                    projFileText = projFile.readlines()
                    projFile.close()
                    if not projFileText :
                        isfileExists = False
                    
                    
                    
                if shouldRun or (not isfileExists):
                    
                    projfile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'wb')
                    total = 0
                    directoryIncreament = 0
                    
                    
                    for ds in self.dtx:
                        directoryIncreament = directoryIncreament + 1 
                        if ds.text().strip() != "":
                            self.checkForChanges(self.projects.currentItem().text(),ds.text(), 'Fixity-'+str(directoryIncreament))
                            orignalPathTextCode = FixityCore.pathCodeEncode(directoryIncreament)
                            changePathTextCode = FixityCore.pathCodeEncode(directoryIncreament)
                            
                            CodeOfPath = ''
                            if self.FileChanged.changeThePathInformation:
                                CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                pathToSaveInManifest = str(ds.text())
                            else:   
                                CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                pathToSaveInManifest = str(str(self.FileChanged.orignalPathText))
                                
                            if(pathToSaveInManifest ==''):
                                pathToSaveInManifest = str(ds.text())
                                CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                
                            if self.FileChanged.changeThePathInformation:
                                self.FileChanged.ReplacementArray[directoryIncreament]= {'orignalpath':self.FileChanged.orignalPathText ,'newPath': self.FileChanged.changePathText,  'orignal':orignalPathTextCode , 'new':changePathTextCode}
                            
                            projfile.write( ( pathToSaveInManifest + "|-|-|" + CodeOfPath + "|-|-|" + str(directoryIncreament) + ";" ) )
                                                             
                    projfile.write("\n")
                    
                    for ms in self.mtx:
                            
                            if ms.text().strip() != "":
                                    projfile.write(ms.text() + ";")
                    projfile.write("\n")
                    projfile.write(str(interval) + " " + self.timer.time().toString() + " " + str(dmonth) + " " + str(dweek) + "\n")
                    
                    projfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                
                    currentProject = self.projects.currentItem().text()
                    
                    Configurations = {}
                    
                    Configurations['RunWhenOnBatteryPower'] = self.runOnlyOnACPower.isChecked() 
                    Configurations['IfMissedRunUponAvailable'] = self.StartWhenAvailable.isChecked()
                    Configurations['onlyonchange'] = self.EmailOnlyWhenSomethingChanged.isChecked()
                    Configurations['RunInitialScan'] = False
                    
                    FixitySchtask.schedule(interval, dweek, dmonth, self.timer.time().toString(), self.projects.currentItem().text(), Configurations,self.SystemInformation)
                    
                    ConfigurationInfo = self.EP.getConfigInfo(currentProject)
                    Allfilters = ConfigurationInfo['filters']
                    Allfilters = str(Allfilters.replace('fil|', '').replace('\n', ''))
                    FiltersArray = Allfilters.split(',')
                    
                    if shouldRun: 
                        for dx in self.dtx:
                            src = dx.text()
                            l = self.buildTable(src, 'sha256')
                            for n in xrange(len(l)):
                                for FA in FiltersArray :
                                    if FA == '' or l[n][1].find(FA) < 0:
                                        projfile.write(l[n][0] + "\t" + l[n][1] + "\t" + l[n][2] + "\n")
                                        total += 1
                     
                    if shouldRun:
                        QMessageBox.information(self, "Fixity", str(total) + " files processed in project: " + self.projects.currentItem().text())
                    else:
                        QMessageBox.information(self, "Fixity", "Settings saved for " + self.projects.currentItem().text())   
                    projfile.close()                     
                else :
                    
                    projfileFileText = []            
                    if isfileExists:            
                        projfileFile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'rb')
                        projfileFileText = projfileFile.readlines()
                        projfileFile.close()
                        configurations = {}
                        configurations['directories'] = ''
                        configurations['emails'] = ''
                        configurations['timingandtype'] = ''
                        
                        directoryIncreament = 0
                        
                        for ds  in self.dtx:
                            directoryIncreament = directoryIncreament + 1 
                            if ds.text().strip() != "":
                                self.checkForChanges(self.projects.currentItem().text(), ds.text(), directoryIncreament)
                                orignalPathTextCode = FixityCore.pathCodeEncode(directoryIncreament)
                                changePathTextCode = FixityCore.pathCodeEncode(directoryIncreament)
                                CodeOfPath = ''

                                if self.FileChanged.changeThePathInformation:
                                    CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                    pathToSaveInManifest = str(ds.text())
                                else:   
                                    CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                    pathToSaveInManifest = str(str(self.FileChanged.orignalPathText))
                                    
                                if(pathToSaveInManifest ==''):
                                    pathToSaveInManifest = str(ds.text())
                                    CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                    
                                if self.FileChanged.changeThePathInformation:
                                    self.FileChanged.ReplacementArray[directoryIncreament]= {'orignalpath':self.FileChanged.orignalPathText ,'newPath': self.FileChanged.changePathText,  'orignal':orignalPathTextCode , 'new':changePathTextCode}
                                
                                configurations['directories'] +=  (pathToSaveInManifest + "|-|-|" + CodeOfPath + "|-|-|" + str(directoryIncreament) + ";")

                        configurations['directories'] += "\n"
                            
                        for ms in self.mtx:
                            if ms.text().strip() != "":
                                configurations['emails']+=str(ms.text()) +str(ms.text()) +";"
                                             
                        configurations['emails'] += "\n"
                        configurations['timingandtype'] = (str(interval) + " " + self.timer.time().toString() + " " + str(dmonth) + " " + str(dweek) + "\n")
                        
                        projfileFileText[0] =  configurations['directories']
                        projfileFileText[1] =  configurations['emails']
                        projfileFileText[2] =  configurations['timingandtype']
                        projfile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'wb')
                        projfile.writelines(projfileFileText)

                        QMessageBox.information(self, "Fixity", "Settings saved for " + self.projects.currentItem().text())
                        
                self.unsaved = False
                return

        # Toggles fields on/off
        def toggler(self, switch):
                for n in xrange(len(self.mtx)):
                    self.mtx[n].setDisabled(switch)
                    self.dtx[n].setDisabled(switch)
                    self.but[n].setDisabled(switch)
                self.timer.setDisabled(switch)
                self.monthly.setDisabled(switch)
                self.weekly.setDisabled(switch)
                self.daily.setDisabled(switch)
                self.timer.setDisabled(switch)
                self.dom.setDisabled(switch)
                self.dow.setDisabled(switch)
                
        
        def changed(self):
                self.unsaved = True
                
        def dayclick(self):
                self.dom.hide()
                self.dow.hide()
                self.spacer.changeSize(30, 25)
                        
        def weekclick(self):
                self.spacer.changeSize(0, 0)
                self.dom.hide()
                self.dow.show()
                
        def monthclick(self):
                self.spacer.changeSize(0, 0)
                self.dow.hide()
                self.dom.show()


        def pickdir(self):
                n = self.but.index(self.sender())
                self.dtx[n].setText(QFileDialog.getExistingDirectory(dir=path.expanduser('~') + '\\Desktop\\'))
                
            
        def replacePathInformation(self):
            projFileChangePath = open('projects\\' + self.projects.currentItem().text()+ 'ChangingPath' + '.fxy', 'wb')    
            currentProjFile = open('projects\\' + self.projects.currentItem().text()+ '.fxy', 'rb')
            
            lineNumber = 1
            for line in currentProjFile:
                lineToWrite = line
                if lineNumber > 4:
                    for SingleReplace in self.FileChanged.ReplacementArray:
                        lineToWrite =line.replace(self.FileChanged.ReplacementArray[SingleReplace]['orignal'], self.FileChanged.ReplacementArray[SingleReplace]['new'])
                projFileChangePath.write(lineToWrite)
                lineNumber = lineNumber+1
            currentProjFile.close()
            projFileChangePath.close()
            
            shutil.copy('projects\\' + self.projects.currentItem().text()+ 'ChangingPath' + '.fxy', 'projects\\' + self.projects.currentItem().text()+ '.fxy')
            remove('projects\\' + self.projects.currentItem().text()+ 'ChangingPath' + '.fxy')
            
            
            
        #Saves And Runs 
        def run(self):
            if all(d.text() == "" for d in self.dtx):
                QMessageBox.warning(self, "Fixity", "No directories selected!\nPlease set directories to scan")
                return
            
            dmonth, dweek = 99, 99
            if self.monthly.isChecked():
                interval = 1
                dmonth = int(self.dom.value())
            elif self.weekly.isChecked():
                interval = 2
                dweek = int(self.dow.currentIndex())
            elif self.daily.isChecked():
                interval = 3
            else:
                QMessageBox.warning(self, "Fixity", "Project schedule not set - please select an interval for scans")
                return
            
            if path.isfile('projects\\' + self.projects.currentItem().text() + '.fxy') and path.isfile('bin\\' + self.projects.currentItem().text() + '-conf.txt'):
                    projectFile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'rb')
                    binFile = open('bin\\' + self.projects.currentItem().text() + '-conf.txt', 'rb')
                    projectFileLines = projectFile.readlines();
                    binFileLines = binFile.readlines();
                    projectFile.close()
                    binFile.close()
                    if (not binFileLines) or (not projectFileLines):
                        QMessageBox.warning(self, "Fixity", "Please save the current project before scanning.")
                        return
                    
            Configurations = {}
                    
            Configurations['RunWhenOnBatteryPower'] = self.runOnlyOnACPower.isChecked() 
            Configurations['IfMissedRunUponAvailable'] = self.StartWhenAvailable.isChecked()
            Configurations['onlyonchange'] = self.EmailOnlyWhenSomethingChanged.isChecked()
            Configurations['RunInitialScan'] = False
                        
            FilePath = getcwd()+'\\schedules\\'
            FixitySchtask.schedule(interval, dweek, dmonth, self.timer.time().toString(), self.projects.currentItem().text(), Configurations,self.SystemInformation)
            FileName = 'AutoFixity.exe';
            params = self.projects.currentItem().text() +' '+'Run'
            
            self.Threading = Threading(self.projects.currentItem().text(), self.projects.currentItem().text(), 1,FileName,FilePath , params)
            
            self.Threading.start()
            QMessageBox.information(self, "Fixity", "Scheduler for Project "+self.projects.currentItem().text() + " is in progress,you will receive an email when process is completed")

        
        #DELETE Given PROJECT 
        def deleteproject(self):
                sbox = QMessageBox()
                try:
                    sbox.setText("Are you certain that you want to delete " + self.projects.currentItem().text() + "?")
                except:
                    QMessageBox.information(self, "Fixity", "No project selected for deletion!")
                    return
                sbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                sbox.setDefaultButton(QMessageBox.Cancel)
                sval = sbox.exec_()
                if sval == QMessageBox.Cancel:
                    return
                try:
                    remove("projects\\" + self.projects.currentItem().text() + ".fxy")
                    remove("schedules\\fixity-" + self.projects.currentItem().text().replace(' ', '_') + ".bat")
                    remove("schedules\\fixity-" + self.projects.currentItem().text().replace(' ', '_') + ".vbs")
                    remove("schedules\\fixity-" + self.projects.currentItem().text().replace(' ', '_') + "-sch.xml")
                    remove("bin\\" + self.projects.currentItem().text() + "-conf.txt")
                except:
                    pass
                
                FixitySchtask.deltask(self.projects.currentItem().text())
                self.projects.takeItem(self.projects.row(self.projects.currentItem()))
                self.unsaved = False
                
                try:
                        self.update(self.projects.selectedItems()[0])
                except:
                        for x in xrange(0, 7):
                                self.dtx[x].setText("")
                                self.mtx[x].setText("")
                        self.monthly.setChecked(True)
                        self.monthclick()
                        self.timer.setTime(QTime(0, 0))
                        self.lastrun.setText("Last checked:")
                self.toggler((self.projects.count() == 0))
                self.unsaved = False
                
        #Fetch All Directory with in this directory 
        def buildTable(self, r, a):
                
                list = []
                fls = []
                
                progress = QProgressDialog()
                progress.setMaximum(100)
                progress.setMinimumDuration(0)
                for root, subFolders, files in walk(r):
                      
                        for file in files:
                                fls.append(path.join(root, file))
                for f in xrange(len(fls)):
                        txt = path.abspath(fls[f])
                        if len(txt) > 43:
                                txt = txt[:20] + '...' + txt[-20:]
                        progress.setLabelText(txt.ljust(43))
                        p = path.abspath(fls[f])
                        h = FixityCore.fixity(p, a)
                        i = FixityCore.ntfsID(p)
                        list.append((h, p, i))
                        progress.setValue(100 * float(f) / len(fls))
                        qApp.processEvents()
                progress.close()
                return list
        
        
        #Update Schedule information 
        def updateschedule(self):
                flagInitialScanUponSaving = False
                isRcipentEmailAddressSet = False
                
                for ms in self.mtx:
                        SingleEmail = ms.text().strip()
                        if  SingleEmail != "":
                            isRcipentEmailAddressSet = True 
                            errorMsg = self.EP.ValidateEmail(SingleEmail)
                            if not str(errorMsg).strip() == 'None':
                                QB = QMessageBox()
                                errorMsg = QB.information(self, "Error", errorMsg)
                                return  
                            
                if isRcipentEmailAddressSet:
                    EmailInfo = self.EP.getConfigInfo()
                    if EmailInfo['email'] == '' or EmailInfo['email'] == '':
                        QMessageBox.information(self, "Email Validation", 'Please configure an email account in the Preferences menu')
                        return
                                
                self.process(flagInitialScanUponSaving)
                
                dmonth, dweek = 99, 99
                if self.monthly.isChecked():
                        interval = 1
                        dmonth = int(self.dom.value())
                elif self.weekly.isChecked():
                        interval = 2
                        dweek = int(self.dow.currentIndex())
                elif self.daily.isChecked():
                        interval = 3
                          
                try: 
                        new = open('projects\\' + self.projects.currentItem().text() + '.tmp.fxy', 'wb')
                        old = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'rb')
                except:
                        QMessageBox.information(self, "Fixity", "No project selected to reschedule!")
                        return
                        
                new.write(old.readline())
                
                for ms in self.mtx:
                        if ms.text().strip() != "":
                                new.write(ms.text() + ";")
                                
                new.write("\n")
                old.readline()
                old.readline()
                new.write(str(interval) + " " + self.timer.time().toString() + " " + str(dmonth) + " " + str(dweek) + "\n")
                while True:
                        x = old.readline()
                        if not x:
                                break
                        new.write(x)
                        
                new.close()
                old.close()
                shutil.copy('projects\\' + self.projects.currentItem().text() + '.tmp.fxy', 'projects\\' + self.projects.currentItem().text() + '.fxy')
                remove('projects\\' + self.projects.currentItem().text() + '.tmp.fxy')
                
                Configurations = {}
                
                Configurations['RunWhenOnBatteryPower'] = self.runOnlyOnACPower.isChecked() 
                Configurations['IfMissedRunUponAvailable'] = self.StartWhenAvailable.isChecked()
                Configurations['onlyonchange'] = self.EmailOnlyWhenSomethingChanged.isChecked()
                Configurations['RunInitialScan'] = False
                
                FixitySchtask.schedule(interval, dweek, dmonth, self.timer.time().toString(), self.projects.currentItem().text() , Configurations,self.SystemInformation)
                self.unsaved = False
        
        #Remove the file which are not required
        def removeNotRequiredFiles(self):
            
            if not str(self.projects.currentItem()) == 'None':
                if path.isfile('projects\\' + self.projects.currentItem().text() + '.fxy') and path.isfile('bin\\' + self.projects.currentItem().text() + '-conf.txt'):
                    projectFile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'rb')
                    binFile = open('bin\\' + self.projects.currentItem().text() + '-conf.txt', 'rb')
                    projectFileLines = projectFile.readlines();
                    binFileLines = binFile.readlines();
                    projectFile.close()
                    binFile.close()
                    if (not binFileLines) or (not projectFileLines):
                        remove('projects\\' + self.projects.currentItem().text() + '.fxy')
                        remove('bin\\' + self.projects.currentItem().text() + '-conf.txt')
                    
            return
       
        #Window close Event
        def closeEvent(self, event):
            if not str(self.projects.currentItem()) == 'None':
                if path.isfile('projects\\' + self.projects.currentItem().text() + '.fxy') and path.isfile('bin\\' + self.projects.currentItem().text() + '-conf.txt'):
                    projectFile = open('projects\\' + self.projects.currentItem().text() + '.fxy', 'rb')
                    binFile = open('bin\\' + self.projects.currentItem().text() + '-conf.txt', 'rb')
                    projectFileLines = projectFile.readlines();
                    binFileLines = binFile.readlines();
                    if (not binFileLines) or (not projectFileLines):
                        self.unsaved = True
                    projectFile.close()
                    binFile.close()
            
            if self.unsaved:
                    sbox = QMessageBox()
                    sbox.setText("There are unsaved changes to this project.")
                    sbox.setInformativeText("These will be discarded when opening a new project.\nWould you like to stay on this project?")
                    sbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Discard)
                    sbox.setDefaultButton(QMessageBox.Ok)
                    sval = sbox.exec_()
                    
                    if sval == QMessageBox.Ok:
                        event.ignore()
                    else:
                        self.removeNotRequiredFiles()
                        event.accept()
                        
        #Check for Difference in root directory in the fixity tool and in manifest                        
        def checkForChanges(self,projectName , searchForPath ,code):
                    directoryIncreament = 0
                    DirectoryDetail = FixityCore.getDirectoryDetail(projectName)
                    try:
                        for ds  in self.dtx:
                            directoryIncreament = directoryIncreament + 1 
                            if ds.text().strip() != "":
                                if(DirectoryDetail[directoryIncreament]  != None and DirectoryDetail[directoryIncreament]  != '' ):
                                    if DirectoryDetail[directoryIncreament][1] != None  and DirectoryDetail[directoryIncreament][1] != '':
                                        pathGiven = FixityCore.getCodePathMore(DirectoryDetail[directoryIncreament][1],DirectoryDetail)
                                    else:
                                        pathGiven = ''
                                else:
                                    pathGiven = ''
                                CodeOfPath = FixityCore.pathCodeEncode(directoryIncreament)
                                if ('Fixity-'+str(code)) == CodeOfPath and pathGiven !=searchForPath:
                                    self.ChangeRootDirectoryInfor(pathGiven , searchForPath )
                    except:
                        pass
                    
if __name__ == '__main__':
        app = QApplication(sys.argv)
        w = ProjectWin(EmailPref , FilterFiles)
        w.show()
        sys.exit(app.exec_())
        