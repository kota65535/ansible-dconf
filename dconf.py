#!/usr/bin/python

import json
import re
import subprocess
import q

from ansible.module_utils.basic import *

def _escape_single_quotes(string):
    return re.sub("'", r"'\''", string)

def _append_value(target, value):
    '''append value to target if the value does not exists'''
    # convert string into list
    try:
        if isinstance(eval(target), list):
            target_list = list(eval(target))
    except Exception:
        target_list = [target]
    try:
        if isinstance(eval(value), list):
            value = list(eval(value))
    except Exception:
        value_list = [value]

    for v in value_list:
        if v not in target_list:
            target_list.append(v)

    return target_list

def _remove_value(target, value):
    '''remove value from target if the value exists'''
    try:
        if isinstance(eval(target), list):
            target_list = list(eval(target))
    except Exception:
        target_list = [target]
    try:
        if isinstance(eval(value), list):
            value = list(eval(value))
    except Exception:
        value_list = [value]

    for v in value_list:
        if v in target_list:
            target_list.remove(v)

    return target_list

def _set_value(user, key, value):

    command = " ".join([
        'export `/usr/bin/dbus-launch`',
        ';',
        '/usr/bin/dconf write', key, "'{0}'".format(_escape_single_quotes(value)),
        ';',
        'kill $DBUS_SESSION_BUS_PID &> /dev/null'
    ])

    q(command)
    return subprocess.check_output([
        'sudo', '-u', user , 'sh', '-c', command
    ]).strip()

def _get_value(user, key):

    command = " ".join([
        'export `/usr/bin/dbus-launch`',
        ';',
        '/usr/bin/dconf read', key,
        ';',
        'kill $DBUS_SESSION_BUS_PID &> /dev/null'
    ])

    return subprocess.check_output([
        'sudo', '-u', user , 'sh', '-c', command
    ]).strip()

def main():

    module = AnsibleModule(
        argument_spec = {
            'state': { 'choices': ['present', 'append', 'absent'], 'default': 'present' },
            'user': { 'required': True },
            'key': { 'required': True },
            'value': { 'required': True },
        },
        supports_check_mode = True,
    )

    params = module.params
    state = module.params['state']
    user = module.params['user']
    key = module.params['key']
    value = module.params['value']

    old_value = _get_value(user, key)
    q(old_value)

    # --- Input value conversion ---
    # list: converted to list object
    # str:  single quotes are stripped
    # int:  do nothing
    try:
        value = eval(value)
    except Exception:
        pass

    if state == 'append':
        value = _append_value(old_value, value)
    elif state == 'absent':
        value = _remove_value(old_value, value)

    # --- Conversion for dconf ---
    # list: converted to str and single quotes added
    # str:  single quotes are added
    # bool: converted to str
    # int:  converted to str
    if isinstance(value, list):
        value = "'{0}'".format(str(value))
    elif isinstance(value, str):
        value = "'{0}'".format(value)
    elif isinstance(value, bool):
        value = 'true' if value else 'false'
    elif isinstance(value, int):
        value = str(value)
    q(value)

    changed = old_value != value

    if changed and not module.check_mode:
        _set_value(user, key, value)

    print json.dumps({
        'changed': changed,
        'key': key,
        'value': value,
        'old_value': old_value,
    })

main()
