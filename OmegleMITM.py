import argparse
import util
from Client import Client

def main(topic):
    util.initLogs()
    client1 = Client(event_delay=1, topics=[topic], name='Stranger 1')
    client2 = Client(event_delay=1, topics=[topic], name='Stranger 2')
    client1.register_other_client(client2)
    client2.register_other_client(client1)

    client1.start()
    util.waitForClient(client1, topic)
    client2.start()

    while client1.isAlive() or client2.isAlive():
        try:
            client1.join(0.1)
            client2.join(0.1)
        except KeyboardInterrupt:
            break

    util.logPrint( 'Disconnecting... ')
    client1.stop()
    client2.stop()

def initArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topic", help="The topic you wanna talk about")
    return parser.parse_args()

if __name__ == '__main__':
    args = initArgs()
    main(args.topic)
    
