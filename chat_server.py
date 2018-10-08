import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ChatServer(object):
    def __init__(self):
        self.users = []
        self.nicknames = []
        self.count = 0

    def join(self, nickname, callback):
        self.valid_nickname(nickname)
        self.users.append((nickname, callback))
        self.nicknames.append(nickname)
        callback._pyroOneway.add('jobdone')
        print('{} JOINED'.format(nickname))
        self.publish('SERVER', '** {} joined **'.format(nickname))
        return [n for (n, c) in self.users]

    def valid_nickname(self, nickname):
        if not nickname: raise ValueError('Enter a nickname')

        if nickname in self.nicknames: raise ValueError('This nickname is already in use')

    def exit(self, nickname):
        for(nick, callback) in self.users:
            if nick == nickname:
                self.users.remove((nick, callback))
                break
        self.publish('SERVER', '** {} left **'.format(nickname))
        self.nicknames.remove(nickname)
        print('{} LEFT'.format(nickname))

    def publish(self, nickname, msg):
        self.count += 1
        for(nick, callback) in self.users[:]:
            try:
                callback.message(self.count, nickname, msg)
            except Pyro4.errors.ConnectionClosedError:
                if(nick, callback) in self.users:
                    self.users.remove((nick, callback))
                    print('Remove dead listener %s %s' % (n, callback))

def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(ChatServer)
    ns.register("chat_server", uri)
    print('Chat server started')
    daemon.requestLoop()

if __name__ == '__main__':
    main()
