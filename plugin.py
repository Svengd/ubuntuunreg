###
# Copyright (c) 2014, Nicolas Coevoet
# Copyright (c) 2017, Unit 193
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import time
import supybot.schedule as schedule
import supybot.world as world
import supybot.ircmsgs as ircmsgs

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('UbuntuUnreg')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class UbuntuUnreg(callbacks.Plugin):
    """send message to #ubuntu-unregged at interval if #ubuntu is +r, do not reload this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(UbuntuUnreg, self)
        self.__parent.__init__(irc)
        schedule.addEvent(self.check,time.time()+self.registryValue('interval'))

    def check(self):
        if world:
            if world.ircs:
                for irc in world.ircs:
                    if '#ubuntu' in irc.state.channels and '#ubuntu-unregged' in irc.state.channels:
                        if 'r' in irc.state.channels['#ubuntu'].modes:
                            irc.queueMsg(ircmsgs.privmsg('#ubuntu-unregged',self.registryValue('message')))
        schedule.addEvent(self.check,time.time()+self.registryValue('interval'))

    def doMode(self,irc,msg):
        channel = msg.args[0]
        if irc.isChannel(channel) and msg.args[1:] and channel in irc.state.channels and channel == '#ubuntu-unregged':
            modes = ircutils.separateModes(msg.args[1:])
            for change in modes:
                (mode,value) = change
                if mode == '+i' and '#ubuntu-unregged' in irc.state.channels:
                    l = []
                    for user in irc.state.channels['#ubuntu-unregged'].users:
                        if not user in irc.state.channels['#ubuntu-unregged'].ops and not user in irc.state.channels['#ubuntu-unregged'].voices:
                            l.append(user)
                    for user in l:
                        irc.queueMsg(ircmsgs.kick('#ubuntu-unregged',user,self.registryValue('kickMessage')))
                    irc.queueMsg(ircmsgs.mode('#ubuntu-unregged', '-i'))

Class = UbuntuUnreg
