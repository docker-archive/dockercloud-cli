class BadParameter(RuntimeError):
    pass


class DockerNotFound(RuntimeError):
    pass


class PublicImageNotFound(RuntimeError):
    pass


class StreamOutputError(Exception):
    pass


class InternalError(RuntimeError):
    pass


class ConfigurationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
