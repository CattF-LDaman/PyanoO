
DEFAULT_CONFIG = {'HOST_PORT':65511,
                  "CRYPTO_KEY":"default_PyanoO",

                  "PRINT_DEBUG_LOGS":False,

                  'SERVER_NAME':'PyanoO Server',

                  'WELCOME_MSG_ENABLED':True,
                  'WELCOME_MSG':'Welcome to {SERVER}, {USER}!',

                  "JOIN_MSG":'{USER} on {ADDR}:{PORT} joined the server.',

                  'MAX_STRIKES':20,

                  "COMMANDS_ENABLED":True,

                  "LOG_MESSAGES_TO_FILE":True,

                  "DEFAULT_ROLE":'User',

                  "MESSAGE_ID_VIEW_PERM_LEVEL":3,

                  }

DEFAULT_ROLES = {'permissions':
    {
    'User':[1,2],
    'Moderator':[1,2,3],
    'Admin':[1,2,3,4],
    'S-Admin':[1,2,3,4,5]
    },
    'hierarchy-low-to-high':['User','Moderator','Admin','S-Admin']
}

DEFAULT_CMD_LEVELS_LIST = {1: ['msg', 'poke'], 2: ['listusers', 'users', 'changepass', 'removepass', 'rempass', 'nopass'], 3: ['listroles', 'roles', 'kick','ban']}  # LEVEL : COMMAND

DEFAULT_CMD_LEVELS = {cmd:level for level,cmds in DEFAULT_CMD_LEVELS_LIST.items() for cmd in cmds}  # COMMAND : LEVEL
