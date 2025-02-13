import logging
import socket
import random
import os

# Check if the user is running under django, and load up
# the awesome settings instead.
if os.environ.get('DJANGO_SETTINGS_MODULE', False):
    from django.conf import settings
else:
    import default_settings as settings

HOST = getattr(settings, 'STATSD_HOST', 'localhost')
PORT = getattr(settings, 'STATSD_PORT', 8125)
RATE = getattr(settings, 'STATSD_SAMPLE_RATE', 1)

class Connection(object):
    '''Statsd Connection

    :keyword host: The statsd host to connect to, defaults to `localhost`
    :keyword port: The statsd port to connect to, defaults to `8125`
    :keyword sample_rate: The sample rate, defaults to `1` (meaning always)
    '''

    def __init__(self, host=None, port=None, sample_rate=None):
        self._host = host or HOST
        self._port = int(port) if port else PORT
        self._sample_rate = sample_rate or RATE
        
        self.logger = logging.getLogger('%s.%s'
            % (__name__, self.__class__.__name__))
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger.debug('Initialized connection to %s:%d with P(%.1f)',
            self._host, self._port, self._sample_rate)

    def send(self, data, sample_rate=None):
        '''Send the data over UDP while taking the sample_rate in account

        The sample rate should be a number between `0` and `1` which indicates
        the probability that a message will be sent. The sample_rate is also
        communicated to `statsd` so it knows what multiplier to use.
        '''
        if sample_rate is None:
            sample_rate = self._sample_rate

        sampled_data = {}
        if sample_rate < 1:
            if random.random() <= sample_rate:
                # Modify the data so statsd knows our sample_rate
                for stat, value in data.iteritems():
                    sampled_data[stat] = '%s|@%s' % (data[stat], sample_rate)
        else:
            sampled_data = data

        try:
            for stat, value in sampled_data.iteritems():
                send_data = '%s:%s' % (stat, value)
                self.udp_sock.sendto(send_data, (self._host, self._port))
        except Exception, e:
            self.logger.exception('unexpected error %r while sending data', e)

    def __repr__(self):
        return '<%s[%s:%d] P(%.1f)>' % (
            self.__class__.__name__,
            self._host,
            self._port,
            self._sample_rate,
        )
