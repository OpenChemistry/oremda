DEFAULT_OREMDA_VAR_DIR = '/run/oremda'
DEFAULT_PLASMA_SOCKET_PATH = f'{DEFAULT_OREMDA_VAR_DIR}/plasma.sock'

OREMDA_FINISHED_QUEUE = '/oremda_finished_queue'

class NodeType:
    Reader = 'reader'
    Source = 'source'
    Operator = 'operator'
    Module = 'module'

class PortType:
    Data = 'data'
    Meta = 'meta'

class IOType:
    In = 'in'
    Out = 'out'

class TaskType:
    Operate = 'operate'
    Terminate = 'terminate'
