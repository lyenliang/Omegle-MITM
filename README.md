Omegle-MITM(Man in the middle attack) is a program that sniffs conversations between two random strangers on Omegle(http://www.omegle.com/), which is a website for you to chat with strangers. It does this by establishing two connections, and then forwarding the messages to one another.

Features:

1. Support 'Common likes': you can specify the common topic fow the two strangers by adding "-t topic". If the program fails to find two strangers with the same topic, it disconnects the stranger.
2. Messages from the two strangers would be recorded into a file named YYYY-MM-DD_HH-MM-SS.log.

Requirements:
 - Python 2.7
 - Python module "mechanize", which can be downloaded at https://pypi.python.org/pypi/mechanize/

Example:

Looking for someone you can chat with...
You're now chatting with a random stranger. Say hi!
Looking for someone you can chat with...
You're now chatting with a random stranger. Say hi!
[Stranger 1] Stranger: hi
[Stranger 2] Stranger is typing...
[Stranger 2] Stranger: bonnie960
 thats my usrname if you want to talk on k _ i _ k
[Stranger 2] Stranger has disconnected.
Disconnecting...
