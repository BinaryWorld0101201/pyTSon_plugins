import sip
sip.setapi('QString', 1)
from ts3plugin import ts3plugin
from random import choice, getrandbits
from PythonQt.QtCore import QTimer, Qt, QUrl#, QString
from PythonQt.QtGui import QWidget, QListWidgetItem, QIcon, QPixmap
from PythonQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bluscream import *
from os import path
from configparser import ConfigParser
from pytson import getPluginPath
from pytsonui import setupUi
from json import load, loads
from traceback import format_exc
import ts3defines, ts3lib, ts3client

class customBadges(ts3plugin):
    name = "Custom Badges"
    apiVersion = 21
    requestAutoload = True
    version = "0.9"
    author = "Bluscream"
    description = "Automatically sets some badges for you :)"
    offersConfigure = True
    commandKeyword = ""
    infoTitle = "[b]Badges[/b]"
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Change " + name, ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Generate Badge UIDs", "")
    ]
    hotkeys = []
    icons = path.join(ts3lib.getConfigPath(), "cache", "badges")
    ini = path.join(getPluginPath(), "scripts", "customBadges", "settings.ini")
    ui = path.join(getPluginPath(), "scripts", "customBadges", "badges.ui")
    badges_local = path.join(getPluginPath(), "include", "badges.json")
    badges_ext = path.join(getPluginPath(), "include", "badges_ext.json")
    badges_remote = "https://gist.githubusercontent.com/Bluscream/29b838f11adc409feac9874267b43b1e/raw"
    badges_ext_remote = "https://raw.githubusercontent.com/R4P3-NET/CustomBadges/master/badges.json"
    cfg = ConfigParser()
    dlg = None
    cfg["general"] = {
        "cfgversion": "1",
        "debug": "False",
        "enabled": "True",
        "badges": "",
        "overwolf": "False",
    }
    badges = {}
    extbadges = {}

    def __init__(self):
        try:
            loadCfg(self.ini, self.cfg)
            self.requestBadges()
            self.requestBadgesExt()
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def infoData(self, schid, id, atype):
        if atype != ts3defines.PluginItemType.PLUGIN_CLIENT: return None
        (err, ownID) = ts3lib.getClientID(schid)
        if ownID != id: return None
        # overwolf = self.cfg.getboolean('general', 'overwolf')
        # badges = self.cfg.get('general', 'badges').split(',')
        (err, badges) = ts3lib.getClientVariable(schid, id, ts3defines.ClientPropertiesRare.CLIENT_BADGES)
        (overwolf, badges) = parseBadges(badges)
        _return = ["Overwolf: {0}".format("[color=green]Yes[/color]" if overwolf else "[color=red]No[/color]")]
        # i = []
        # for badge in badges:
            # if badge
        for badge in badges:
            lst = self.badges
            if badge in self.extbadges: lst = self.extbadges
            _return.append("{} {}".format(
                "[img]https://badges-content.teamspeak.com/{}/{}.svg[/img]".format(badge, lst[badge]["filename"] if badge in lst else "unknown"),
                self.badgeNameByUID(badge, lst) if badge in lst else badge
            ))
        return _return

    def badgeNameByUID(self, uid, lst=badges):
        for badge in lst:
            if badge == uid: return lst[badge]["name"]

    def requestBadges(self):
        try:
            with open(self.badges_local, encoding='utf-8-sig') as json_file:
                self.badges = load(json_file)
        except:
            self.nwmc = QNetworkAccessManager()
            self.nwmc.connect("finished(QNetworkReply*)", self.loadBadges)
            self.nwmc.get(QNetworkRequest(QUrl(self.badges_remote)))

    def requestBadgesExt(self):
        try:
            with open(self.badges_ext, encoding='utf-8-sig') as json_file:
                self.extbadges = load(json_file)
        except:
            self.nwmc_ext = QNetworkAccessManager()
            self.nwmc_ext.connect("finished(QNetworkReply*)", self.loadBadgesExt)
            self.nwmc_ext.get(QNetworkRequest(QUrl(self.badges_ext_remote)))

    def loadBadgesExt(self, reply):
        try:
            data = reply.readAll().data().decode('utf-8')
            self.extbadges = loads(data)
            print("extbadges: {}".format(self.extbadges))
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{}".format(self.badges))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def loadBadges(self, reply):
        try:
            # print(reply)
            _reason = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            _reasonmsg = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute)
            print('reason={}|reasonmsg={}'.format(_reason,_reasonmsg))
            data = reply.readAll().data().decode('utf-8')
            self.badges = loads(data)
            print("badges: {}".format(self.badges))
            if PluginHost.cfg.getboolean("general", "verbose"): ts3lib.printMessageToCurrentTab("{}".format(self.badges))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def stop(self):
        saveCfg(self.ini, self.cfg)

    def configure(self, qParentWidget):
        self.openDialog()

    def parseLocalBadges(self):
        db = ts3client.Config()
        q = db.query("SELECT * FROM Badges") #  WHERE key = BadgesListData
        timestamp = 0
        ret = b""
        while q.next():
            key = q.value("key")
            print("DB: Key: {}".format(key))
            if key == "BadgesListTimestamp":
                timestamp = q.value("value")
                print("{} Type: {}".format(key, type(timestamp)))
            elif key == "BadgesListData":
                ret = q.value("value")
                print("{} Type: {}".format(key, type(ret)))
        del db
        return timestamp, ret

    def readBadge(self, badges, start=0):
        next = 12
        ret = []
        guid_len = 0
        guid = ""
        name_len = 0
        name = ""
        url_len = 0
        url = ""
        desc_len = 0
        desc = ""
        try:
            for i in range(start, badges.size()):
                if i == next: #guid_len
                    guid_len = int(badges.at(i))
                    print("#", i, "GUID Length:", guid_len)
                    guid = str(badges.mid(i+1, guid_len))
                    print("#", i, "GUID:", guid)
                elif i == (next + 1 + guid_len + 1):
                    name_len = int(badges.at(i))
                    print("#", i, "Name Length:", name_len)
                    name = str(badges.mid(i+1, name_len))
                    print("#", i, "Name:", name)
                elif i == (next + 1 + guid_len + 1 + name_len + 2):
                    url_len = int(badges.at(i))
                    print("#", i, "URL Length:", url_len)
                    url = str(badges.mid(i+1, url_len))
                    print("#", i, "URL:", url)
                elif i == (next + 1 + guid_len + 1 + name_len + 2 + url_len + 2):
                    desc_len = int(badges.at(i))
                    print("#", i, "DESC Length:", desc_len)
                    desc = str(badges.mid(i+1, desc_len))
                    print("#", i, "DESC:", desc)
                    ret.append({"guid": guid, "name": name, "url": url, "description": desc})
                    next = (next + guid_len + 2 + name_len + 2 + url_len + 2 + desc_len + 13)
                    print(next)
        except: print("error")
        return ret

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype != ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL: return
        if menuItemID == 0: self.openDialog()
        elif menuItemID == 1:
            (timestamp, badges) = self.parseLocalBadges()
            print("Timestamp:", timestamp)
            print("Badges:", badges.data())
            print(self.readBadge(badges, 0))
            return
            for i in range(0,3):
                # 0c4u2snt-ao1m-7b5a-d0gq-e3s3shceript
                uid = [random_string(size=8, chars=string.ascii_lowercase + string.digits)]
                for _i in range(0,3):
                    uid.append(random_string(size=4, chars=string.ascii_lowercase + string.digits))
                uid.append(random_string(size=12, chars=string.ascii_lowercase + string.digits))
                ts3lib.printMessageToCurrentTab("[color=red]Random UID #{}: [b]{}".format(i, '-'.join(uid)))

    def onConnectStatusChangeEvent(self, schid, newStatus, errorNumber):
        if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            self.setCustomBadges()

    def setCustomBadges(self):
        try:
            overwolf = self.cfg.getboolean('general', 'overwolf')
            badges = self.cfg.get('general', 'badges').split(",")
            # if len(badges) > 0: badges += ['0c4u2snt-ao1m-7b5a-d0gq-e3s3shceript']
            (err, schids) = ts3lib.getServerConnectionHandlerList()
            for schid in schids:
                sendCommand(self.name, buildBadges(badges, overwolf), schid)
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def openDialog(self):
        if not self.dlg: self.dlg = BadgesDialog(self)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()

class BadgesDialog(QWidget):
    listen = False
    def __init__(self, customBadges, parent=None):
        try:
            super(QWidget, self).__init__(parent)
            setupUi(self, customBadges.ui)
            self.cfg = customBadges.cfg
            self.ini = customBadges.ini
            self.icons = customBadges.icons
            self.badges = customBadges.badges
            self.extbadges = customBadges.extbadges
            self.setCustomBadges = customBadges.setCustomBadges
            self.requestBadges = customBadges.requestBadges
            self.requestBadgesExt = customBadges.requestBadgesExt
            self.setAttribute(Qt.WA_DeleteOnClose)
            self.setWindowTitle("Customize Badges")
            self.setupList()
            self.listen = True
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def badgeItem(self, badge, alt=False, ext=False):
        try:
            lst = self.extbadges if ext else self.badges
            item = QListWidgetItem(lst[badge]["name"])
            item.setData(Qt.UserRole, badge)
            try: item.setToolTip(lst[badge]["description"])
            except: pass
            try: item.setIcon(QIcon("{}\\{}{}".format(self.icons, lst[badge]["filename"],"_details" if alt else "")))
            except: pass
            return item
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def updatePreview(self, uid, i):
        try:
            if uid in self.badges: lst = self.badges
            elif uid in self.extbadges: lst = self.extbadges
            # (QPixmap::fromImage(image.scaled(200,200))
            filename = "{}\\{}_details".format(self.icons, lst[uid]["filename"])
            if i == 0:
                self.badge1.setPixmap(QPixmap(filename).scaled(60,60))
            elif i == 1:
                self.badge2.setPixmap(QPixmap(filename).scaled(60,60))
            elif i == 2:
                self.badge3.setPixmap(QPixmap(filename).scaled(60,60))
        except:
            ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def setupList(self):
        try:
            self.chk_overwolf.setChecked(True if self.cfg.getboolean('general', 'overwolf') else False)
            self.lst_available.clear()
            for badge in self.badges:
                self.lst_available.addItem(self.badgeItem(badge))
            self.grp_available.setTitle("{} Available (Internal)".format(len(self.badges)))
            self.lst_available_ext.clear()
            for badge in self.extbadges:
                self.lst_available_ext.addItem(self.badgeItem(badge, False, True))
            self.grp_available_ext.setTitle("{} Available (External)".format(len(self.extbadges)))
            badges = self.cfg.get('general', 'badges').split(",")
            if len(badges) < 1: return
            self.lst_active.clear()
            i = 0
            for badge in badges:
                if not badge: return
                if i < 3: self.updatePreview(badge, i)
                i += 1
                if badge in self.badges:
                    self.lst_active.addItem(self.badgeItem(badge))
                elif badge in self.extbadges:
                    self.lst_active.addItem(self.badgeItem(badge, False, True))
            self.grp_active.setTitle("{} Active".format(self.lst_active.count))
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def updateBadges(self):
        try:
            items = []
            self.badge1.clear();self.badge2.clear();self.badge3.clear();
            for i in range(self.lst_active.count):
                 uid = self.lst_active.item(i).data(Qt.UserRole)
                 items.append(uid)
                 if i < 3: self.updatePreview(uid, i)
            self.grp_active.setTitle("{} Active".format(self.lst_active.count))
            self.cfg.set('general', 'badges', ','.join(items))
            self.setCustomBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)


    def addActive(self, ext=False):
        try:
            item = self.lst_available_ext.currentItem() if ext else self.lst_available.currentItem()
            self.lst_active.addItem(self.badgeItem(item.data(Qt.UserRole), False, True if ext else False))
            if self.chk_autoApply.checkState() == Qt.Checked:
                self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def delActive(self):
        try:
            row = self.lst_active.currentRow
            self.lst_active.takeItem(row)
            if self.chk_autoApply.checkState() == Qt.Checked:
                self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_lst_available_doubleClicked(self, mi):
        if not self.listen: return
        self.addActive()

    def on_btn_addactive_clicked(self):
        if not self.listen: return
        self.addActive()

    def on_lst_available_ext_doubleClicked(self, mi):
        if not self.listen: return
        self.addActive(True)

    def on_btn_addactive_ext_clicked(self):
        if not self.listen: return
        self.addActive(True)

    def on_lst_active_doubleClicked(self, mi):
        if not self.listen: return
        self.delActive()

    def on_btn_removeActive_clicked(self):
        if not self.listen: return
        self.delActive()

    def on_btn_removeAll_clicked(self):
        if not self.listen: return
        if not confirm("Custom Badge", "Remove all active badges?"): return
        self.lst_active.clear()
        if self.chk_autoApply.checkState() == Qt.Checked:
            self.updateBadges()

    def on_chk_overwolf_stateChanged(self, mi):
        if not self.listen: return
        try:
            self.cfg.set('general', 'overwolf', "True" if mi == Qt.Checked else "False")
            self.updateBadges()
        except: ts3lib.logMessage(format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_lst_active_indexesMoved(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_lst_active_itemChanged(self, mi):
        if not self.listen: return
        self.updateBadges()

    def on_btn_apply_clicked(self):
        if not self.listen: return
        self.updateBadges()

    def on_btn_save_clicked(self):
        if not self.listen: return
        saveCfg(self.ini, self.cfg)

    def on_btn_reload_clicked(self):
        if not self.listen: return
        self.requestBadges()
        self.requestBadgesExt()
        self.setupList()

    def on_btn_close_clicked(self):
        self.close()
