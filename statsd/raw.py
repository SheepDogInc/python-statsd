import statsd

class Raw(statsd.Client):
    '''Statsd "Raw" Object
    
    See pull request: https://github.com/etsy/statsd/pull/13
    that describes storing discrete values as a discrete value.
    
    This is based on the timer method for now until statsd actually
    supports the Raw type, and the author Erik Kastner suggests that
    we just re-use the Timer "ms" datatype to store raw / discrete
    values.
    
    Additional documentation is available at the
    parent class :class:`~statsd.client.Client`


    >>> raw = Raw('raw_value')
    >>> raw.push(10)
    '''

    def _send(self, value, subname=None):
        """
        Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
        client name)
        :keyword delta: The delta to add to/remove from the counter
        """
        
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %d', name, value)
        return statsd.Client._send(self, {name: '%d|ms' % value})
        
    def push(self, value):
        """
        Set the value of the raw key
        """
        self._value = value
        return self._send(value)

def set_raw_key(key, value):
    return Raw(key).push(value)

raw = set_raw_key
discrete = set_raw_key

if __name__ == '__main__':
    import doctest
    doctest.testmod()

