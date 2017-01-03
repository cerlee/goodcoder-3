#!/usr/bin/env python
#coding:gbk
#Copyright (c) Baidu.com, Inc. All Rights Reserved
#author:haoguanguan(@baidu.com)

import Schduler

if __name__ == "__main__":
    print '*'*30
    print "Schduler start"
    print '*'*30
    thread = Schduler.MyThread()
    thread.set_func()
    thread.run()
