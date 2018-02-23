# -*- coding: utf-8 -*-
"""
@author: H
"""
from importlib import import_module
import os
import base64
from github import Github
import login_info

#import mpyq module, replay file, decode build number from protocol


def import_heroprotocol(protocol_name):
    try:
        prot = import_module(protocol_name)
        
    except ImportError:
        g = Github(login_info.user, login_info.password)

        for item in g.get_user().get_starred():
            if item.name == 'heroprotocol':
                cont = item.get_file_contents(protocol_name)
                data = base64.b64decode(cont.content)


                with open(os.path.join('C:/Users/admin/HotS_Replay_Decode/heroprotocol27/',protocol_name), 'w') as f:
                    f.write(data)
        prot = import_module('heroprotocol27.{}'.format(protocol_name[:-3]))
    return prot

