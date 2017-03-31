from yowsup.common.tools import Jid
from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_chatstate.protocolentities import OutgoingChatstateProtocolEntity
from yowsup.layers.protocol_presence                   import protocolentities
from yowsup.layers.protocol_presence.protocolentities  import AvailablePresenceProtocolEntity, \
    UnavailablePresenceProtocolEntity
import time
from random import randrange

class SyncLayer(YowInterfaceLayer):

    def __init__(self):
        super(SyncLayer, self).__init__()
        file = open("group1", "r")
        value = file.readlines()
        if value[1] != "":
            self.group1 = value[1]
            self.group1f = value[2]
        else:
            print("need to set group 1")
            self.group1 = ""
            self.group1f = ""
        file.close()

        file = open("group2", "r")
        value = file.readlines()
        if value[1] != "":
            self.group2 = value[1]
            self.group2f = value[2]
        else:
            print("need to set group 1")
            self.group2 = ""
            self.group2f = ""
        file.close()

        self.sent_to = 0
        self.sent_to_false = 0
        print("start")

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        print("got message")
        self.sent_to = 0
        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)

            #TODO: set groups name if files, add admin support
            if (messageProtocolEntity.getTimestamp() >= int(time.time()) - 10):
                if (messageProtocolEntity.isGroupMessage()):
                    if not self.group1 and "group 1" in messageProtocolEntity.getBody():
                        print("set group 1")
                        self.group1 = messageProtocolEntity.getFrom()
                        self.group1f = messageProtocolEntity.getFrom(False)
                    elif not self.group2 and "group 2" in messageProtocolEntity.getBody():
                        print("set group 2")
                        self.group2 = messageProtocolEntity.getFrom()
                        self.group2f = messageProtocolEntity.getFrom(False)
                    elif self.group1 == messageProtocolEntity.getFrom() and self.group2:
                        self.sent_to = self.group2
                        self.sent_to_false = self.group2f
                    elif self.group2 == messageProtocolEntity.getFrom() and self.group1:
                        self.sent_to = self.group1
                        self.sent_to_false = self.group1f
                else:

                    self.sent_to = messageProtocolEntity.getFrom()
                    self.sent_to_false = messageProtocolEntity.getFrom(False)
            else:
                print("Ignoring old message")
                self.sent_to = 0

        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)
            self.sent_to = 0

        time.sleep(randrange(3, 7) * 0.1)
        self.toLower(messageProtocolEntity.ack()) # set recieved (double v)
        time.sleep(randrange(3, 7) * 0.1)
        self.toLower(AvailablePresenceProtocolEntity()) # set online
        time.sleep(randrange(3, 7) * 0.1)
        self.toLower(messageProtocolEntity.ack(True))   # set read (blue)
        time.sleep(randrange(3, 7) * 0.1)
        if self.sent_to:
            self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_TYPING,
                                                         Jid.normalize(self.sent_to_false))) # set in writing
            time.sleep(randrange(15, 25) * 0.1)
            self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_PAUSED,
                                                         Jid.normalize(self.sent_to_false))) # set no is writing
            time.sleep(randrange(7, 13) * 0.1)
            self.toLower(messageProtocolEntity.forward(self.sent_to)) # send message
            time.sleep(randrange(25, 35) * 0.1)
        self.toLower(UnavailablePresenceProtocolEntity()) # set offline

        self.sent_to = 0



    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def onTextMessage(self,messageProtocolEntity):
        # just print info
        print("Echoing %s to %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))
        if (messageProtocolEntity.isGroupMessage()):
            print("(GROUP)[%s]-[%s]\t%s" % (messageProtocolEntity.getParticipant(), messageProtocolEntity.getFrom(), messageProtocolEntity.getBody()))
        else:
            print("(PVT)[%s]\t%s" % (messageProtocolEntity.getFrom(), messageProtocolEntity.getBody()))

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "vcard":
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))


