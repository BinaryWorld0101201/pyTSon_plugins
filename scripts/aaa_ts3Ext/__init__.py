import ts3lib
from ts3plugin import ts3plugin, PluginHost
from pytson import getCurrentApiVersion
from bluscream import timestamp, GroupType, log
from ts3Ext import ts3SessionHost, logLevel
from ts3defines import *

class aaa_ts3Ext(ts3plugin):
    name = "aaa_ts3Ext"
    try: apiVersion = getCurrentApiVersion()
    except: apiVersion = 22
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "ts3Ext library implementation"
    offersConfigure = False
    commandKeyword = "ext"
    infoTitle = None
    menuItems = []
    hotkeys = []
    guiLogLvl = logLevel.NONE
    banned_names = ["BAN", "NOT WELCOME"]
    mod_names = ["MOD", "OPERATOR", "ADMIN"] # TODO CHECK
    tabs =  {}

    def __init__(self):
        self.ts3host = ts3SessionHost(self)
        err, schids = ts3lib.getServerConnectionHandlerList()
        for schid in schids:
            (err, status) = ts3lib.getConnectionStatus(schid)
            self.onConnectStatusChangeEvent(schid, status, err)
        log(self, LogLevel.LogLevel_DEBUG, "{0}[color=orange]{1}[/color] Plugin for pyTSon by [url=https://github.com/{2}]{2}[/url] loaded.".format(timestamp(), self.name, self.author), 0)

    def processCommand(self, schid, keyword):
            args = keyword.split(' ')
            cmd = args.pop(0).lower()
            if cmd == "dump":
                print(self.tabs)
            else: return False
            return True

    def onConnectStatusChangeEvent(self, schid, status, errorNumber):
        if status == ConnectStatus.STATUS_CONNECTION_ESTABLISHED:
            srv = self.ts3host.getServer(schid)
            self.tabs[schid] = {
                "channelBanGroup": None,
                "channelModGroup": None,
                "srv": srv,
            }
            err, self.tabs[schid]["name"] = ts3lib.getServerVariable(schid, VirtualServerProperties.VIRTUALSERVER_NAME)
            err, self.tabs[schid]["host"], self.tabs[schid]["port"], self.tabs[schid]["pw"] = ts3lib.getServerConnectInfo(schid)
            self.tabs[schid]["address"] = '{}:{}'.format(self.tabs[schid]["host"], self.tabs[schid]["port"]) if hasattr(self.tabs[schid], 'port') else self.tabs[schid]["host"]
            err, self.tabs[schid]["clid"] = ts3lib.getClientID(schid)
            err, self.tabs[schid]["nick"] = ts3lib.getClientSelfVariable(schid, ClientProperties.CLIENT_NICKNAME) # ts3lib.getClientVariable(schid, self.tabs[schid]["clid"], ClientProperties.CLIENT_NICKNAME)
            err, self.tabs[schid]["nick_phonetic"] = ts3lib.getClientSelfVariable(schid, ClientPropertiesRare.CLIENT_NICKNAME_PHONETIC)
            err, self.tabs[schid]["uid"] = ts3lib.getClientSelfVariable(schid, ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            err, self.tabs[schid]["token"] = ts3lib.getClientSelfVariable(schid, ClientPropertiesRare.CLIENT_DEFAULT_TOKEN)
            err, self.tabs[schid]["cid"] = ts3lib.getChannelOfClient(schid, self.tabs[schid]["clid"])
            err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"] = ts3lib.getChannelConnectInfo(schid, self.tabs[schid]["cid"])
            srv.requestServerGroupList()
            srv.requestChannelGroupList()
        elif status == ConnectStatus.STATUS_DISCONNECTED:
            if schid in self.tabs: self.tabs[schid]["status"] = status

    def onServerGroupListEvent(self, schid, serverGroupID, name, atype, iconID, saveDB):
        if atype != GroupType.REGULAR: return
        srv = self.ts3host.getServer(schid)
        srv.updateServerGroup(serverGroupID, name, iconID)

    def onChannelGroupListEvent(self, schid, channelGroupID, name, atype, iconID, saveDB):
        if atype != GroupType.REGULAR: return
        tab = self.tabs[schid]
        for _name in self.banned_names:
            if _name in name.upper():
                tab["channelBanGroup"] = channelGroupID
                break
        for _name in self.mod_names:
            if _name in name.upper():
                tab["channelModGroup"] = channelGroupID
                break
        srv = self.ts3host.getServer(schid)
        srv.updateChannelGroup(channelGroupID, name, iconID)

    def onTalkStatusChangeEvent(self, schid, status, isReceivedWhisper, clientID):
        self.ts3host.getServer(schid).updateTalkStatus(clientID, status, isReceivedWhisper)

    def onClientMoveEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, moveMessage):
        if schid not in self.tabs: return
        if clientID != self.tabs[schid]["clid"]: return
        self.tabs[schid]["cid"] = newChannelID
        (err, self.tabs[schid]["cpath"], self.tabs[schid]["cpw"]) = ts3lib.getChannelConnectInfo(schid, newChannelID)

    def onClientSelfVariableUpdateEvent(self, schid, flag, oldValue, newValue):
        if schid not in self.tabs: return
        if flag == ClientProperties.CLIENT_NICKNAME:
            self.tabs[schid]["nick"] = newValue
        elif flag == ClientPropertiesRare.CLIENT_NICKNAME_PHONETIC:
            self.tabs[schid]["nick_phonetic"] = newValue
        elif flag == ClientProperties.CLIENT_UNIQUE_IDENTIFIER:
            self.tabs[schid]["uid"] = newValue
        elif flag == ClientPropertiesRare.CLIENT_DEFAULT_TOKEN:
            self.tabs[schid]["token"] = newValue

    def onPacketOut(self, msg, schid):
        if schid in self.tabs:
            if msg.startswith("clientinit "):
                self.tabs[schid]["clientinit"] = msg
        return False, msg

    def stop(self): del self.ts3host