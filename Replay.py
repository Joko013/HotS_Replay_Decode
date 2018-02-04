# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 17:32:31 2017

@author: H
"""
from mpyq import MPQArchive
from heroprotocol27 import protocol46889 as protocol
from importlib import import_module


class Replay(object):
    
    def __init__(self, filename):
        self.build = None
        self.map_name = None
        self.player_list = None
        self.match_length_seconds = None
        self.players_dead = None
        self.tracker_events = None
        self.filename = filename
                
    def decode_replay(self):
           
        
        mpq = MPQArchive(self.filename)
        
        #import correct protocol
        protocol = import_module('heroprotocol27.protocol47479')
        header = protocol.decode_replay_header(mpq.header['user_data_header']['content'])
        build_number = header['m_version']['m_baseBuild']
        module_name = 'heroprotocol27.protocol{}'.format(build_number)
        protocol = import_module(module_name)
        
        #player list
        details = protocol.decode_replay_details(mpq.read_file('replay.details'))
        self.player_list = details['m_playerList']
        
        self.tracker_events = protocol.decode_replay_tracker_events(
            mpq.read_file('replay.tracker.events')
            )
        
        born = []
        died = [{'name': self.filename , 'gameloop': 0 }]
        
        for event in self.tracker_events:    
            #log name and unit tag of a born hero unit
            if event['_event'] == 'NNet.Replay.Tracker.SUnitBornEvent' and 'Hero' in event['m_unitTypeName']:
                born.append({'unit_tag': protocol.unit_tag(event['m_unitTagIndex'], \
                                                   event['m_unitTagRecycle']), 'name': event['m_unitTypeName']})
                continue

            #check if event is unit died event
            if event['_event'] <> 'NNet.Replay.Tracker.SUnitDiedEvent':
                continue
    
            #for each unit died event check if the unit was a hero, if so append to 'died' list
            for item in born:
                if protocol.unit_tag(event['m_unitTagIndex'],event['m_unitTagRecycle']) == item['unit_tag']:
                    died.append({'name': item['name'], 'gameloop': event['_gameloop']/16})
                    continue
        self.players_dead = died
        return self.players_dead