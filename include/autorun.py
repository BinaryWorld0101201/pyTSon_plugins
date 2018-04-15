import os, json, configparser, webbrowser, traceback, urllib.parse, ts3defines, itertools
from datetime import datetime
from ts3lib import *
from ts3plugin import *
from pytsonui import *
from devtools import *
from PythonQt.QtGui import *
from PythonQt.QtCore import *
from PythonQt.QtNetwork import *
from PythonQt.Qt import *
from PythonQt.private import *
from PythonQt.QtSql import *
from PythonQt.QtUiTools import *
from bluscream import *

self = QApplication.instance()
def log(message, channel=ts3defines.LogLevel.LogLevel_INFO, server=0):
    message = str(message)
    _f = '[{:%H:%M:%S}]'.format(datetime.now())+" ("+str(channel)+") "
    if server > 0:
        _f += "#"+str(server)+" "
    _f += "Console> "+message
    logMessage(message, channel, "pyTSon Console", server)
    printMessageToCurrentTab(_f)
    # if PluginHost.shell:
    #     PluginHost.shell.appendLine(_f)
    print(_f)

def toggle(boolean):
    boolean = not boolean
    return boolean

def getitem(useList, name): #getitem(PluginHost.modules,'devTools')
    for _name,value in useList.items():
        if _name == name: return value

def alert(message, title="pyTSon"):
    _a = QMessageBox()
    _a.show()

urlrequest = False
def url(url):
    try:
        from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest
        #if urlrequest: return
        urlrequest = QNetworkAccessManager()
        urlrequest.connect("finished(QNetworkReply*)", urlResponse)
        urlrequest.get(QNetworkRequest(QUrl(url)))
    except:
        from traceback import format_exc
        try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon::autorun", 0)
        except: print("Error in autorun: "+format_exc())
def urlResponse(reply):
    try:
        from PythonQt.QtNetwork import QNetworkReply
        if reply.error() == QNetworkReply.NoError:
            print("Error: %s (%s)"%(reply.error(), reply.errorString()))
            print("Content-Type: %s"%reply.header(QNetworkRequest.ContentTypeHeader))
            print("<< reply.readAll().data().decode('utf-8') >>")
            print("%s"%reply.readAll().data().decode('utf-8'))
            print("<< reply.readAll().data() >>")
            print("%s"%reply.readAll().data())
            print("<< reply.readAll() >>")
            print("%s"%reply.readAll())
            return reply
        else:
            err = logMessage("Error checking for update: %s" % reply.error(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon.PluginHost.updateCheckFinished", 0)
            if err != ts3defines.ERROR_ok:
                print("Error checking for update: %s" % reply.error())
        urlrequest.delete()
        urlrequest = None
    except:
        from traceback import format_exc
        try: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon::autorun", 0)
        except: print("Error in autorun: "+format_exc())
def unlock(show=False):
    for item in self.allWidgets():
        try: item.setEnabled(True)
        except: pass
        try: item.setCheckable(True)
        except: pass
        try: item.setDragEnabled(True)
        except: pass
        try: item.setDragDropMode(QAbstractItemView.DragDrop)
        except: pass
        try: item.setSelectionMode(QAbstractItemView.MultiSelection)
        except: pass
        try: item.setSelectionBehavior(QAbstractItemView.SelectItems)
        except: pass
        try: item.setResizeMode(QListView.Adjust)
        except: pass
        try: item.setSortingEnabled(True)
        except: pass
        try:
            if item.ContextMenuPolicy() == Qt.PreventContextMenu:
                item.setContextMenuPolicy(Qt.NoContextMenu)
        except: pass
        try:
            if "background:red;" in item.styleSheet:
                item.styleSheet = item.styleSheet.replace("background:red;", "")
        except: logMessage("error", ts3defines.LogLevel.LogLevel_INFO, "QSS", 0);pass
        try: item.setTextInteractionFlag(Qt.TextEditable)
        except: pass
        try: item.setUndoRedoEnabled(True)
        except: pass
        try: item.setReadOnly(False)
        except: pass
        try: item.clearMinimumDateTime()
        except: pass
        try: item.clearMaximumDateTime()
        except: pass
        try: item.clearMinimumTime()
        except: pass
        try: item.clearMaximumTime()
        except: pass
        try: item.clearMinimumDate()
        except: pass
        try: item.clearMaximumDate()
        except: pass
        try: item.setDateEditEnabled(True)
        except: pass
        try: item.setTextVisible(True)
        except: pass
        try: item.setHeaderHidden(False)
        except: pass
        try: item.setItemsExpandable(True)
        except: pass
        try: item.setModality(Qt.NonModal)
        except: pass
        if show:
            try: item.setHidden(False)
            except: pass
            try: item.show()
            except: pass
            try: item.raise_()
            except: pass
            try: item.activateWindow()
            except: pass
def lock(show=False):
    for item in self.allWidgets():
        try: item.setEnabled(False)
        except: pass
        try: item.setCheckable(False)
        except: pass
        try: item.setDragEnabled(False)
        except: pass
        try: item.setDragDropMode(QAbstractItemView.NoDragDrop)
        except: pass
        try: item.setSelectionMode(QAbstractItemView.NoSelection)
        except: pass
        try: item.setSelectionBehavior(QAbstractItemView.SelectItems)
        except: pass
        try: item.setResizeMode(QListView.Adjust)
        except: pass
        try: item.setResizeMode(QHeaderView.Interactive)
        except: pass
        try: item.setSectionResizeMode(QHeaderView.Interactive)
        except: pass
        try: item.setSortingEnabled(False)
        except: pass
        try: item.setContextMenuPolicy(Qt.PreventContextMenu)
        except: pass
        try: item.styleSheet = ""
        except: pass
        try: item.setTextInteractionFlag(Qt.NoTextInteraction)
        except: pass
        try: item.setUndoRedoEnabled(False)
        except: pass
        try: item.setReadOnly(True)
        except: pass
        try: item.setDateEditEnabled(True)
        except: pass
        try: item.setTextVisible(True)
        except: pass
        try: item.setHeaderHidden(False)
        except: pass
        try: item.setItemsExpandable(True)
        except: pass
        try: item.setModality(Qt.ApplicationModal)
        except: pass
        try: item.clicked.disconnect()
        except: pass
        if show:
            try: item.setHidden(True)
            except: pass

def findWidget(name):
    try:
        name = name.lower()
        widgets = self.topLevelWidgets()
        widgets = widgets + self.allWidgets()
        ret = dict()
        c = 0
        for x in widgets:
            c += 1
            if name in x.objectName.lower() or name in str(x.__class__).lower():
                ret["class:"+str(x.__class__)+str(c)] = "obj:"+x.objectName;continue
            if hasattr(x, "text"):
                if name in x.text.lower():
                    ret["class:"+str(x.__class__)+str(c)] = "obj:"+x.objectName
        return ret
    except:
        print("error")
def widgetbyclass(name):
    ret = []
    widgets = self.topLevelWidgets()
    widgets = widgets + self.allWidgets()
    for x in widgets:
        if name in str(x.__class__).replace("<class '","").replace("'>",""):
            ret.extend(x)
    return ret
def widgetbyobject(name):
    name = name.lower()
    widgets = self.topLevelWidgets()
    widgets = widgets + self.allWidgets()
    for x in widgets:
        if str(x.objectName).lower() == name:
            return x
def getobjects(name, cls=True):
    import gc
    objects = []
    for obj in gc.get_objects():
        if (isinstance(obj, QObject) and
            ((cls and obj.inherits(name)) or
             (not cls and obj.objectName() == name))):
            objects.append(obj)
    return objects

def objects():
    import gc;_ret = []
    for x in gc.get_objects(): _ret.extend(str(repr(x)))
    return _ret

def file(name, content):
    with open(os.path.expanduser("~/Desktop/"+name+".txt"), "w") as text_file:
        print(str(content), file=text_file)

def generateAvatarFileName():
    (error, ownID) = getClientID(schid)
    (error, ownUID) = getClientVariableAsString(schid, ownID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
    ownUID = ownUID.encode('ascii')
    from base64 import b64encode
    return "avatar_"+b64encode(ownUID).decode("ascii").split('=')[0]

def getItems(object):
    return [(a, getattr(object, a)) for a in dir(object)
            if not a.startswith('__') and not callable(getattr(object, a)) and not "ENDMARKER" in a and not "DUMMY" in a]

def getvar(clid):
    for name, var in getItems(ConnectionProperties) + getItems(ConnectionPropertiesRare):
        ret = "=== Results for {0} ===\n".format(name)
        try:
            (err, var1) = getConnectionVariableAsDouble(schid, clid, var)
            (er, ec) = getErrorMessage(err)
            ret += "getConnectionVariableAsDouble: err={0} var={1}\n".format(ec, var1)
        except Exception as e:
            ret += "getConnectionVariableAsDouble err={0}\n".format(e)
        try:
            (err, var2) = getConnectionVariableAsUInt64(schid, clid, var)
            (er, ec) = getErrorMessage(err)
            ret += "getConnectionVariableAsUInt64: err={0} var={1}\n".format(ec, var2)
        except Exception as e:
            ret += "getConnectionVariableAsUInt64 err={0}\n".format(e)
        try:
            (err, var3) = getConnectionVariableAsString(schid, clid, var)
            (er, ec) = getErrorMessage(err)
            ret += "getConnectionVariableAsString: err={0} var={1}\n".format(ec, var3)
        except Exception as e:
            ret += "getConnectionVariableAsString err={0}\n".format(e)
        print("{0}================".format(ret))

#if error == 0:
    #error, ownnick = getClientDisplayName(schid, ownid)
    # if error == 0:
    #     def p(c, cmd="test", clid=0):
    #         if c == 0:
    #             print("Sent command "+cmd+" to PluginCommandTarget_CURRENT_CHANNEL")
    #         elif c == 1:
    #             print("Sent command "+cmd+" to PluginCommandTarget_SERVER")
    #         elif c == 2:
    #             print("Sent command "+cmd+" to PluginCommandTarget_CLIENT")
    #             sendPluginCommand(schid, cmd, c, [clid])
    #             return
    #         elif c == 3:
    #             print("Sent command "+cmd+" to PluginCommandTarget_CURRENT_CHANNEL_SUBSCRIBED_CLIENTS")
    #         elif c == 4:
    #             print("Sent command "+cmd+" to PluginCommandTarget_MAX")
    #         sendPluginCommand(schid, cmd, c, [])

schid = getCurrentServerConnectionHandlerID()
(_e, ownid) = getClientID(schid)

print('(pyTSon Console started at: {:%Y-%m-%d %H:%M:%S})'.format(datetime.now()))
for item in sys.path:
    print('"'+item+'"')
print("")
print(sys.flags)
print("")
print(sys.executable+" "+sys.platform+" "+sys.version+" API: "+str(sys.api_version))
print("")

class testClass(object):
    def __init__(): pass
    def testFunction(): pass
