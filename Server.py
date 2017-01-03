#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved
#author:haoguanguan(@baidu.com)

class Node(object):
    """
    the abstruct of node:
        type, ip, port
    """
    def __init__(self, node_ip, node_port, node_type, con_sock):
        self._ip = node_ip
        self._port = node_port
        self._type = node_type
        self._sock = con_sock

    def get_ipport(self):
        """
        get node ip and port
        """
        return (self._ip, self._port)

    def get_sock(self):
        """
        get sock fd od node
        """
        return self._sock

    def get_type(self):
        """
        get the type of node
        """
        return self._type




