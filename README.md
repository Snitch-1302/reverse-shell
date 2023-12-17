# reverse-shell
Simple python implementation of a reverse shell.

A reverse shell attack is a type of attack in which an attacker gains control over a compromised system by establishing a connection from the victim's machine to the attacker's machine. To create a reverse shell, the attacker sets up a listener on their machine to receive the connection from the victim's machine. Once the connection is established, the attacker can execute commands on the victim's machine and control it remotely.
Reverse shell attacks are often used by attackers to carry out malicious activities, such as stealing data, installing malware, or carrying out other types of attacks.

Here, Python is the programming language used and socket programming is done to establish connection between client and server. The server also supports connection from multiple clients and could listen to unto 5 clients. Multithreading is also implemented here for faster execution by assigning thread 1 to create, bind and accept the connections and thread 2 for executing the command client side. Python’s subprocess module is used to run shell commands in the server system.

