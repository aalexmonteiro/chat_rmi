import sys
import Pyro4
import threading

class ChatClient(object):
    def __init__(self):
        self.chat_server = Pyro4.core.Proxy('PYRONAME:chat_server')
        self.abort=0

    @Pyro4.expose
    @Pyro4.oneway
    def message(self, number_msg, nickname, msg):
        if nickname != self.nickname:
            print('MESSAGE {}-[{}] {}'.format(number_msg, nickname, msg))

    def start(self):
        self.nickname = input('Choose a nickname: ').strip()
        people = self.chat_server.join(self.nickname, self)
        print('Joined chat as {}'.format(self.nickname))
        print('People on this chat: {}'.format(', '.join(people)))
        print('Ready to talk!')
        print('Type /quit to quit')
        try:
            self.send_action()
        finally:
            self.exit()

    def send_action(self):
        while not self.abort:
            line = input('> ').strip()
            if line == '/quit':
                break
            if line:
                self.chat_server.publish(self.nickname, line)

    def exit(self):
        self.chat_server.exit(self.nickname)
        self.abort = 1
        self._pyroDaemon.shutdown()

class DaemonThread(threading.Thread):
	def __init__(self, chat_client):
		threading.Thread.__init__(self)
		self.chat_client = chat_client
		self.setDaemon(True)

	def run(self):
		with Pyro4.core.Daemon() as daemon:
			daemon.register(self.chat_client)
			daemon.requestLoop(lambda: not self.chat_client.abort)

def main():
    chat_client = ChatClient()
    dt = DaemonThread(chat_client)
    dt.start()
    chat_client.start()
    print('Exit.')

if __name__ == '__main__':
    main()
