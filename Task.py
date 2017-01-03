#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved
#author:haoguanguan(@baidu.com)

import json

class Client(object):
    """
    the asbtruct of cli which is only exsit in Task
    """
    def __init__(self, cli_ip, cli_port, cli_sock):
        self.cip = cli_ip
        self.cport = cli_port
        self.csock = cli_sock


class Task(object):
    """
    the abstruct of task
    """
    Env = ("GCC3", "GCC4", "WINDOWS")
    def __init__(self, cli_ip, cli_port, cli_sock, task_json):
        self._cli_msg = Client(cli_ip, cli_port, cli_sock)
        # the _task_msg is like:{"env":"GCC", "c":"cd"}
        self._task_msg = task_json
        self._task_msg = self.check_arg()
        if self._task_msg.has_key('version'):
            self.csock.send("Sc version 1.0.0.0")
            self._task_msg = {}

    def get_module(self):
        """
        return the module name
        """
        return self._task_msg["module"]

    def get_sock(self):
        """
        return the client sock
        """
        return self._cli_msg.csock

    def get_task_msg(self):
        """
        return a str of task msg
        """
        return json.dumps(self._task_msg)

    def get_type(self):
        """
        return type of this compile
        """
        return self._task_msg["env"]



    def check_arg(self):
        """
        check the arg:
            v : print version and ignore other arg
            env/e: if empty: error, if not in Env: show not support
            m: module which I want to compile
            o:point out the output location
            c:no request
            other:show not support
        """
        res_map = {}
        for arg in self._task_msg:
            if arg in ("v", "vrsion"):
                return {'version':''}
            elif arg in ("env", "e"):
                if self._task_msg[arg] is "" or self._task_msg[arg] not in Task.Env:
                    print '[Error]:env is not safety'
                    return {}
                else:
                    res_map["env"] = self._task_msg[arg]
            elif arg in ("m", "module"):
                if self._task_msg[arg] is "":
                    print '[Error]:module is empty'
                    return {}
                else:
                    res_map['module'] = self._task_msg[arg]
            elif arg in ("o", "output"):
                if self._task_msg[arg] is "":
                    print '[Error]:output is empty'
                    return {}
                else:
                    res_map['output'] = self._task_msg[arg]
            elif arg in ("c", "cmd"):
                if self._task_msg[arg] is "":
                    print '[Error]:cmd is empty'
                    return {}
                else:
                    res_map["cmd"] = self._task_msg[arg]
            else:
                print '[WARN]:', arg, 'is not supported now and ignored'
        return res_map
