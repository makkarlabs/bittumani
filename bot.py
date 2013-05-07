#!/usr/bin/env python
# This code was written for Python 3.1.1
# version 0.101
 
# Changelog:
# version 0.100
# Basic framework
#
# version 0.101
# Fixed an error if an admin used a command with an argument, that wasn't an admin-only command
 
import socket, sys, threading, time
 
# Hardcoding the root admin - it seems the best way for now
root_admin = "abhiin1947"
 
# Defining a class to run the server. One per connection. This class will do most of our work.
class IRC_Server:
 
    # The default constructor - declaring our global variables
    # channel should be rewritten to be a list, which then loops to connect, per channel.
    # This needs to support an alternate nick.
    def __init__(self, host, port, nick, channel , password = "ronaldo"):
        self.irc_host = host
        self.irc_port = port
        self.irc_nick = nick
        self.irc_channel = channel
        self.irc_sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.is_connected = False
        self.should_reconnect = False
        self.command = ""
 
   
    # This is the bit that controls connection to a server & channel.
    # It should be rewritten to allow multiple channels in a single server.
    # This needs to have an "auto identify" as part of its script, or support a custom connect message.
    def connect(self):
        self.should_reconnect = True
        try:
            self.irc_sock.connect ((self.irc_host, self.irc_port))
        except:
            print ("Error: Could not connect to IRC; Host: " + str(self.irc_host) + "Port: " + str(self.irc_port))
            exit(1) # We should make it recconect if it gets an error here
        print ("Connected to: " + str(self.irc_host) + ":" + str(self.irc_port))
       
        str_buff = ("NICK %s \r\n") % (self.irc_nick)
        self.irc_sock.send (str_buff.encode())
        print ("Setting bot nick to " + str(self.irc_nick) )
       
        str_buff = ("USER %s 8 * :X\r\n") % (self.irc_nick)
        self.irc_sock.send (str_buff.encode())
        print ("Setting User")
        # Insert Alternate nick code here.
       
        # Insert Auto-Identify code here.
       
        str_buff = ( "JOIN %s \r\n" ) % (self.irc_channel)
        self.irc_sock.send (str_buff.encode())
        print ("Joining channel " + str(self.irc_channel) )
        self.is_connected = True
        self.listen()
   
    def listen(self):
        while self.is_connected:
            recv = self.irc_sock.recv( 4096 )
            if str(recv).find ( "PING" ) != -1:
                self.irc_sock.send ( "PONG ".encode() + recv.split() [ 1 ] + "\r\n".encode() )
            if str(recv).find ( "PRIVMSG" ) != -1:
                irc_user_nick = str(recv).split ( '!' ) [ 0 ] . split ( ":")[1]
                irc_user_host = str(recv).split ( '@' ) [ 1 ] . split ( ' ' ) [ 0 ]
                irc_user_message = self.data_to_message(str(recv))
                print ( irc_user_host + " :: " + irc_user_nick + ": " + irc_user_message)
                # "!" Indicated a command
                if ( len(irc_user_message) > 0 and str(irc_user_message[0]) == "!" ):
                    self.command = str(irc_user_message[1:])
                    # (str(recv)).split()[2] ) is simply the channel the command was heard on.
                    self.process_command(irc_user_nick, ( (str(recv)).split()[2] ) )
        if self.should_reconnect:
            self.connect()
   
    def data_to_message(self,data):
        data = data[data.find(':')+1:len(data)]
        data = data[data.find(':')+1:len(data)]
        data = str(data[0:len(data)-2])
        return data
       

    # This function sends a message to a channel, which must start with a #.
    def send_message_to_channel(self,data,channel):
        print ( ( "%s: %s") % (self.irc_nick, data) )
        self.irc_sock.send( (("PRIVMSG %s :%s\r\n") % (channel, data)).encode() )
   
    # This function takes a channel, which must start with a #.
    def join_channel(self,channel):
        if (channel[0] == "#"):
            str_buff = ( "JOIN %s \r\n" ) % (channel)
            self.irc_sock.send (str_buff.encode())
            # This needs to test if the channel is full
            # This needs to modify the list of active channels
           
    # This function takes a channel, which must start with a #.
    def quit_channel(self,channel):
        if (channel[0] == "#"):
            str_buff = ( "PART %s \r\n" ) % (channel)
            self.irc_sock.send (str_buff.encode())
            # This needs to modify the list of active channels
   
       
    # This nice function here runs ALL the commands.
    # For now, we only have 2: root admin, and anyone.
    def process_command(self, user, channel):
        # This line makes sure an actual command was sent, not a plain "!"
        if ( len(self.command.split()) == 0):
            return
        # So the command isn't case sensitive
        command = (self.command).lower()
        # Break the command into pieces, so we can interpret it with arguments
        command = command.split()
       
        # All admin only commands go in here.
        if (user == root_admin):
            # The first set of commands are ones that don't take parameters
            if ( len(command) == 1):
 
                #This command shuts the bot down.    
                if (command[0] == "quit"):
                    str_buff = ( "QUIT %s \r\n" ) % (channel)
                    self.irc_sock.send (str_buff.encode())
                    self.irc_sock.close()
                    self.is_connected = False
                    self.should_reconnect = False
                   
            # These commands take parameters
            else:
               
                # This command makes the bot join a channel
                # This needs to be rewritten in a better way, to catch multiple channels
                if (command[0] == "join"):
                    if ( (command[1])[0] == "#"):
                        irc_channel = command[1]
                    else:
                        irc_channel = "#" + command[1]
                    self.join_channel(irc_channel)
                   
                # This command makes the bot part a channel
                # This needs to be rewritten in a better way, to catch multiple channels
                if (command[0] == "part"):
                    if ( (command[1])[0] == "#"):
                        irc_channel = command[1]
                    else:
                        irc_channel = "#" + command[1]
                    self.quit_channel(irc_channel)
 
               
        # All public commands go here
        # The first set of commands are ones that don't take parameters
        if ( len(command) == 1):
       
            if (command[0] == "hi"):
                self.send_message_to_channel( ("Hello to you too, " + user), channel )
            if (command[0] == "panni"):
                self.send_message_to_channel( ("Please do not use bad words in this group(unless using those words to abuse KarSub :P) " + user), channel )
            if (command[0] == "stupidsql"):
                self.send_message_to_channel( ("insert into forward_contracts (spot_rate, carrying_cost, margin, timestamp) values ('53.05', '0.75','0.1', now());"), channel )
            if ("poda" in command[0] and "ng" in command[0]):
                self.send_message_to_channel( ("** Start Music!! **"), channel )
            if (command[0] == "whoami"):
                self.send_message_to_channel( user, channel )
            if (command[0].lower() == "whoru" or command[0].lower() == "whoareu" or command[0].lower() == "whoareyou"):
                self.send_message_to_channel( "The only bittumani!", channel )
            if (command[0] == ":'(" or command[0] == "cry"):
                self.send_message_to_channel( "It's okay " + user + " everything will be just fine. :)", channel )
            if (command[0] == "hedgerepo"):
                self.send_message_to_channel( "stockscrape: https://github.com/makkarlabs/stockscrape.git ", channel )
                self.send_message_to_channel( "hedge_jobs: https://bitbucket.org/the_real_slim_karthik/hedge_jobs", channel )
                self.send_message_to_channel( "hedge_app: https://bitbucket.org/yeskarthik/hedge_app",channel )
            if (command[0] == "stepstocompile"):
                self.send_message_to_channel( "1. Clone all 3 repos(type !hedgerepo)", channel )
                self.send_message_to_channel( "2. Copy default_config to config.py. Modify config.py in those repos(set mysql auth etc)", channel )
                self.send_message_to_channel( "3. Execute all files in hedge_jobs *important*", channel )
                self.send_message_to_channel( "4. Goto hedge_app folder and open python terminal", channel )
                self.send_message_to_channel( "5. 'from hedge_app import db'", channel )
                self.send_message_to_channel( "6. 'db.create_all()'", channel )
                self.send_message_to_channel( "7. Open mysql terminal", channel )
                self.send_message_to_channel( "8. Execute mysql query(type !stupidsql) *important*", channel )
                self.send_message_to_channel( "9. python runserver.py", channel )
                self.send_message_to_channel( "10. Thank Abhinandan for creating this wonderful tutorial :P", channel )
            if(command[0] == "amigoodboy"):
                if(user == "abhiin1947"):
                    self.send_message_to_channel( "You are the best! :D", channel )
                else:
                    self.send_message_to_channel( "panni! bad boy!!! :-|", channel )
        else:
            
            if (command[0] == "bop"):
                self.send_message_to_channel( ("\x01ACTION bopz " + str(command[1]) + "\x01"), channel )
           
 
# Here begins the main programs flow:

test = IRC_Server("irc.freenode.net", 6667, "bittumani", "#makkarlabs")
run_test = threading.Thread(None, test.connect)
run_test.start()
 
while (test.should_reconnect):
    time.sleep(5)