from yowsup.common.tools import Jid
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_chatstate.protocolentities import OutgoingChatstateProtocolEntity
# from yowsup.layers.protocol_presence import protocolentities
from yowsup.layers.protocol_presence.protocolentities import AvailablePresenceProtocolEntity, \
    UnavailablePresenceProtocolEntity
import time
from random import randrange
import os.path


class SyncLayer(YowInterfaceLayer):

    def __init__(self):
        super(SyncLayer, self).__init__()
        self.group = [["", ""], ["", ""]]
        self.sent_to = ["", ""]
        self.admin = [""]
        self.isGroupSet = [self.initGroupName(1), self.initGroupName(2)]
        self.initAdmin()
        self.startTime = int(time.time())
        print("start in " + str(self.startTime))

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        print("got message")
        self.sent_to[0] = ""
        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)

            # TODO: set groups name if files, add admin support
            if messageProtocolEntity.getTimestamp() >= self.startTime - 10:
                if messageProtocolEntity.isGroupMessage():
                    if self.isGroupSet != [1, 1]:
                        if "group 1" in messageProtocolEntity.getBody():
                            self.setGroupName(1, messageProtocolEntity)
                            self.isGroupSet[0] = 1
                            pass
                        elif "group 2" in messageProtocolEntity.getBody():
                            self.setGroupName(2, messageProtocolEntity)
                            self.isGroupSet[1] = 1
                            pass

                        if self.isGroupSet[0] == 0:
                            print("need to set group 1")
                        if self.isGroupSet[1] == 0:
                            print("need to set group 2")
                    else:
                        if messageProtocolEntity.getFrom() == self.group[0][0]:
                            self.sent_to = self.group[1]
                            # self.sent_to_false = self.group2f
                        elif messageProtocolEntity.getFrom() == self.group[1][0]:
                            self.sent_to = self.group[0]
                            # self.sent_to_false = self.group1f
                else:
                    if "live" in messageProtocolEntity.getBody() or "חיים" in messageProtocolEntity.getBody():
                        self.sent_to[0] = messageProtocolEntity.getFrom()
                        self.sent_to[1] = messageProtocolEntity.getFrom(False)
                    elif "set admin" in messageProtocolEntity.getBody():
                        self.setAdmin(messageProtocolEntity.getFrom())
                    elif "reset group" in messageProtocolEntity.getBody() \
                            and messageProtocolEntity.getFrom() in self.admin:
                        self.resetGroups()
            else:
                print("Ignoring old message")
                self.sent_to[0] = ""

        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)
            self.sent_to[0] = ""

        time.sleep(randrange(3, 7) * 0.1)
        self.toLower(messageProtocolEntity.ack())  # set received (double v)
        time.sleep(randrange(3, 7) * 0.1)
        self.toLower(AvailablePresenceProtocolEntity())  # set online
        time.sleep(randrange(3, 7) * 0.1)
        self.toLower(messageProtocolEntity.ack(True))  # set read (blue)
        time.sleep(randrange(3, 7) * 0.1)
        if self.sent_to[0] != "":
            self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_TYPING,
                                                         Jid.normalize(self.sent_to[1])))  # set in writing
            time.sleep(randrange(15, 25) * 0.1)
            self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_PAUSED,
                                                         Jid.normalize(self.sent_to[1])))  # set no is writing
            time.sleep(randrange(7, 13) * 0.1)
            self.toLower(messageProtocolEntity.forward(self.sent_to[0]))  # send message
            time.sleep(randrange(25, 35) * 0.1)
        self.toLower(UnavailablePresenceProtocolEntity())  # set offline

        self.sent_to[0] = ""

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    @staticmethod
    def onTextMessage(messageProtocolEntity):
        # just print info
        print("%s: Echoing %s to %s" % (str(messageProtocolEntity.getTimestamp()), messageProtocolEntity.getBody(),
                                        messageProtocolEntity.getFrom(False)))
        if messageProtocolEntity.isGroupMessage():
            print("(GROUP)[%s]-[%s]\t%s" % (messageProtocolEntity.getParticipant(), messageProtocolEntity.getFrom(),
                                            messageProtocolEntity.getBody()))
        else:
            print("(PVT)[%s]\t%s" % (messageProtocolEntity.getFrom(), messageProtocolEntity.getBody()))

    @staticmethod
    def onMediaMessage(messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(),
                                                       messageProtocolEntity.getLongitude(),
                                                       messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "vcard":
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(),
                                                    messageProtocolEntity.getCardData(),
                                                    messageProtocolEntity.getFrom(False)))

    def initGroupName(self, groupNum):
        if os.path.exists("group" + str(groupNum)):
            file = open("group" + str(groupNum), "r")
            value = file.readlines()
            if value[0] != "":
                print("set group " + str(groupNum))
                self.group[groupNum - 1][0] = value[0]
                self.group[groupNum - 1][1] = value[1]
            file.close()
            return 1
        return 0

    def setGroupName(self, groupNum, messageProtocolEntity):
        print("set group " + str(groupNum))
        self.group[groupNum - 1][0] = messageProtocolEntity.getFrom()
        self.group[groupNum - 1][1] = messageProtocolEntity.getFrom(False)
        file = open("group" + str(groupNum), "w")
        file.write(self.group[groupNum - 1][0] + "\n" + self.group[groupNum - 1][1])
        file.close()

    def initAdmin(self):
        if os.path.exists("admin"):
            file = open("admin", "r")
            value = file.readlines()
            for admin in value:
                print("set admin " + admin)
                self.admin.append(admin)
            file.close()
            return 1
        return 0

    def setAdmin(self, admin):
        print("set admin :" + admin)
        self.admin.append(admin)
        file = open("admin", "w+")
        file.write(admin + "\n")
        file.close()

    def resetGroups(self):
        print("reset groups")
        self.isGroupSet = [0, 0]
        f = open("group1", "w")
        f.write("")
        f.close()
        f = open("group2", "w")
        f.write("")
        f.close()
