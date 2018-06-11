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

import supybot.world as world
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.schedule as schedule

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('UbuntuUnreg')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class UbuntuUnreg(callbacks.Plugin):
    """Send message to #ubuntu-unregged at interval if #ubuntu is +r."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(UbuntuUnreg, self)
        self.__parent.__init__(irc)
        self.event = 'UbuntuUnreg'
        schedule.addPeriodicEvent(self.check, self.registryValue('interval'), self.event)

    def die(self):
        schedule.removePeriodicEvent(self.event)

    def check(self):
        for irc in world.ircs:
            if '#ubuntu' in irc.state.channels and '#ubuntu-unregged' in irc.state.channels:
                if 'r' in irc.state.channels['#ubuntu'].modes:
                    irc.queueMsg(ircmsgs.privmsg('#ubuntu-unregged', self.registryValue('message')))

    def doMode(self, irc, msg):
        channel = msg.args[0]
        if channel == '#ubuntu-unregged' and channel in irc.state.channels:
            modes = ircutils.separateModes(msg.args[1:])
            for (mode, value) in modes:
                if mode == '+i':
                    kicks = []
                    for user in irc.state.channels[channel].users:
                        if not (user in irc.state.channels[channel].ops or user in irc.state.channels[channel].voices):
                            kicks.append(user)
                    if 'r' in irc.state.channels[channel].modes:
                        for user in kicks:
                            irc.queueMsg(ircmsgs.IrcMsg('REMOVE #ubuntu-unregged %s :%s' % (user, self.registryValue('kickMessage'))))
                        irc.queueMsg(ircmsgs.mode(channel, '-ir'))
                    else:
                        for user in kicks:
                            irc.queueMsg(ircmsgs.kick(channel, user, self.registryValue('kickMessage')))
                        irc.queueMsg(ircmsgs.mode(channel, '-i'))

Class = UbuntuUnreg
