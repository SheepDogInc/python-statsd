import logging
import statsd


class Client(object):
    '''Statsd Client Object

    :param task_id: see :attr:`name`.
    :param task_id: see :attr:`connection`.
    '''

    #: The name of the client, everything sent from this client will be \
    #: prefixed by name
    name = None

    #: The :class:`~statsd.connection.Connection` to use, creates a new connection if no \
    #: connection is given
    connection = None

    def __init__(self, name, connection=None):
        self.name = name
        if not connection:
            connection = statsd.Connection()
        self.connection = connection
        self.logger = logging.getLogger('%s.%s'
            % (__name__, self.__class__.__name__))

    @classmethod
    def _get_name(cls, *name_parts):
        def to_str(value):
            if isinstance(value, unicode):
                value = value.encode('utf-8', 'replace')
            return value

        name_parts = [to_str(x) for x in name_parts if x]
        return '.'.join(name_parts)

    def get_client(self, name=None, class_=None):
        '''Get a (sub-)client with a separate namespace
        This way you can create a global/app based client with subclients
        per class/function

        :keyword name: The name to use, if the name for this client was `spam`
            and the `name` argument is `eggs` than the resulting name will be
            `spam.eggs`
        :keyword class_: The :class:`~statsd.client.Client` subclass to use (e.g.
            :class:`~statsd.Timer` or :class:`~statsd.counter.Counter`)
        '''

        # If the name was given, use it. Otherwise simply clone
        name = self._get_name(self.name, name)

        # Create using the given class, or the current class
        if not class_:
            class_ = self.__class__

        return class_(
            name=name,
            connection=self.connection,
        )

    def __repr__(self):
        return '<%s:%s@%r>' % (
            self.__class__.__name__,
            self.name,
            self.connection,
        )

    def _send(self, data):
        return self.connection.send(data)

