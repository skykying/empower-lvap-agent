#ifndef CHATTERSOCKET_HH
#define CHATTERSOCKET_HH
#include <click/element.hh>
#include <click/error.hh>

/*
=c

ChatterSocket("TCP", PORTNUMBER [, I<KEYWORDS>])
ChatterSocket("UNIX", FILENAME [, I<KEYWORDS>])

=s debugging

reports chatter messages to connected sockets

=io

None

=d

Opens a chatter socket that allows other user-level programs to receive copies
of router chatter traffic. Depending on its configuration string,
ChatterSocket will listen on TCP port PORTNUMBER, or on a UNIX-domain socket
named FILENAME.

The "server" (that is, the ChatterSocket element) simply echoes any messages
generated by the router configuration to any existing "clients". The server
does not read any data from its clients.

When a connection is opened, ChatterSocket responds by stating its protocol
version number with a line like "Click::ChatterSocket/1.0\r\n". The current
version number is 1.0.

ChatterSocket broadcasts copies of messages generated by the default
ErrorHandler or the C<click_chatter> function. Most elements report messages
or run-time errors using one of these mechanisms.

Keyword arguments are:

=over 8

=item CHANNEL

Word. The chatter channel: the socket generates messages sent to this channel.
Default is the default channel, which corresponds to C<click_chatter>.

Channels help you organize extensive debugging output. For example, you could
send extremely verbose messages to a `C<verbose>' channel, then only connect
to that channel when you want verbosity.

To send messages to a particular channel, you should fetch the ErrorHandler
object corresponding to that channel, using the Router member function
C<Router::chatter_channel(const String &channel_name)>.

=item QUIET_CHANNEL

Boolean. Messages sent to a non-default channel are not normally printed on
standard error. If QUIET_CHANNEL is false, however, its messages do go to
standard error, along with chatter messages. Default is true.

=item GREETING

Boolean. Determines whether the C<Click::ChatterSocket/1.0> greeting is sent.
Default is true.

=back

=e

  ChatterSocket(unix, /tmp/clicksocket);

=a ControlSocket */

class ChatterSocket : public Element { public:

  ChatterSocket();
  ~ChatterSocket();

  const char *class_name() const	{ return "ChatterSocket"; }
  ChatterSocket *clone() const		{ return new ChatterSocket; }
  
  int configure_phase() const		{ return CONFIGURE_PHASE_INFO; }
  int configure(const Vector<String> &conf, ErrorHandler *);
  int initialize(ErrorHandler *);
  void uninitialize();

  void selected(int);

  void handle_text(ErrorHandler::Seriousness, const String &);
  void flush();

 private:

  String _unix_pathname;
  int _socket_fd;
  String _channel;
  bool _greeting : 1;

  Vector<String> _messages;
  Vector<uint32_t> _message_pos;
  uint32_t _max_pos;
  
  Vector<int> _fd_alive;
  Vector<uint32_t> _fd_pos;
  int _live_fds;

  static const char *protocol_version;

  int flush(int fd, int min_useful_message);

};

inline void
ChatterSocket::handle_text(ErrorHandler::Seriousness, const String &message)
{
  if (_live_fds && message.length()) {
    _messages.push_back(message);
    _message_pos.push_back(_max_pos);
    _max_pos += message.length();
    flush();
  }
}

#endif
