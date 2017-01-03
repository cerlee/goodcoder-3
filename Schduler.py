#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved
#author:haoguanguan(@baidu.com)


import threading
import Queue
import socket
import Server
import Task
import json
import select


class MyThread(object):
    """
    the Schduler main entery
    """
    def __init__(self):
        self._threadid = []
        self._schduler = Schduler()

    def set_func(self):
        """
        set two thread func:deal and wait
        """
        handle1 = threading.Thread(target=Schduler.wait, args=(self._schduler, ))
        self._threadid.append(handle1)
        handle2 = threading.Thread(target=Schduler.deal, args=(self._schduler, ))
        self._threadid.append(handle2)

    def run(self):
        """
        start thread and join it
        """
        for thread_id in self._threadid:
            print '[NOTICE]:start one thread, ', thread_id
            thread_id.start()
        for thread_id in self._threadid:
            thread_id.join()

class MyQueue(object):
    """
    define a lock queue
    """
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def append(self, item):
        """
        append item
        """
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()

    def pop(self, index = -1):
        """
        pop item
        """
        self.lock.acquire()
        if index < 0:
            tmp_res = self.queue.pop()
        else:
            tmp_res = self.queue.pop(index)
        self.lock.release()
        return tmp_res

    def size(self):
        """
        get size of queue
        """
        self.lock.acquire()
        res_len = len(self.queue)
        self.lock.release()
        return res_len

    def get_queue(self):
        """
        get queue for foreach
        """
        return self.queue

class Schduler(object):
    """
    the abstruct of schduler:
        nodes, tasks,
    """
    def __init__(self):
        self._nodes = MyQueue()
        # 30 tasks
        self._tasks = MyQueue()
        self._map = {}
        # current deal node ip && cli ip
        self._output_map_table = {}
        # schduler msg
        self._ip_port = ('127.0.0.1', 8001)
        self._sock_id = 0
        # read set for select
        self._read_set = []
        print 'schduler ip is 127.0.0.1, port is 8801'

    def get_task(self, module):
        """
        according to module get the task
        """
        for item in self._tasks:
            if module == item.get_module():
                return item
        return None


    def exchange_msg(self, str_msg, con_sock):
        """
        pass the output msg to cli
        """
        # get the dest sock
        sock = self._output_map_table[con_sock]
        if sock is not None:
            sock.send(str_msg)
            self._output_map_table.pop(con_sock)
            self._read_set.remove(con_sock)
            self._read_set.remove(sock)
            sock.close()
            con_sock.close()
        else:
            print '[Error]:cannot find the maping relation between node with cli'


    def judge_json(self, json_data, con_sock):
        """
        get the json data like:
            {"NODES":env}
            {"TASKS":task}
            {"OUPUT":msg}
        """
        print '[NOTICE]:get data is', json_data
        tuple_addr = con_sock.getsockname()
        if json_data.has_key("NODES"):
            node = Server.Node(tuple_addr[0], tuple_addr[1], json_data["NODES"], con_sock)
            self._nodes.append(node)
        elif json_data.has_key("TASKS"):
            task = Task.Task(tuple_addr[0], tuple_addr[1], con_sock, json_data["TASKS"])
            if task.get_task_msg() != dict():
                self._tasks.append(task)
            else:
                task.get_sock().close()
        elif json_data.has_key("OUTPUT"):
            self.exchange_msg(json_data["OUTPUT"], con_sock)
        else:
            print "[Error]:the msg is not a node or task"

    def do_read(self, con_sock):
        """
        read json data and push
        """
        json_data = ""
        tmp_data = ""
        while True:
            tmp_data = con_sock.recv(20)
            for i in range(len(tmp_data)):
                if tmp_data[i] != '#':
                    json_data += tmp_data[i]
                else:
                    # get json str and push into queue
                    self.judge_json(json.loads(json_data), con_sock)
                    json_data = ""
            if len(tmp_data) < 20:
                break

    def wait(self):
        """
        wait for task and node
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(self._ip_port)
        sock.listen(5)
        self._read_set.append(sock)
        time_out = 20
        while True:
            read_res, write_res, exce_res = select.select(self._read_set, [], [], time_out)
            if not (read_res or write_res or exce_res):
                print '[WARN]:time out:20  no connected msg arrived'
                continue
            for read_handle in read_res:
                if read_handle == sock:
                    con_sock, addr = sock.accept()
                    print '[NOTICE]:', addr, 'connect successfully'
                    self._read_set.append(con_sock)
                else:
                    self.do_read(read_handle)

    def deal(self):
        """
        get a node and task for compile
        _map = {module:(ip, port)}
        """
        while True:
            if self._nodes.size() == 0:
               continue
            node = self._nodes.pop()
            # find task from _map
            ip_port = node.get_ipport()
            task = None
            for module in self._map:
                if ip_port is self._map[module]:
                    task = self.get_task(module)

            if task is None:
                # not find in _map than find in _tasks
                node_env = node.get_type()
                for item in self._tasks.get_queue():
                    if node_env == item.get_type():
                        task = item

            if task is None:
                node.get_sock().send("{}")
            else:
                node.get_sock().send(task.get_task_msg())
                self.map_add(node, task)
                self._output_map_table[node.get_sock()] = task.get_sock()

    def map_add(self, node, task):
        """
        add it into map
        """
        self._map[task.get_module()] = node.get_ipport()
