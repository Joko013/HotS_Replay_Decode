# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 17:32:31 2017

@author: H
"""
from mpyq import MPQArchive
from heroprotocol27 import protocol46889 as protocol
from importlib import import_module
import os
import csv
#import mpyq module, replay file, decode build number from protocol
import mpyq
import pandas as pd
from import_heroprotocol import import_heroprotocol      
    



class Replays_list(object):
    
    def __init__(self):
        self._all_stats = []
        self._replays_path = os.path.join(os.getcwd(),'Replays')
        self._replays = []
        for (dirpath, dirnames, filenames) in os.walk(self._replays_path):
            self._replays.extend(filenames)
            break
            
    def replay_stats(self):
        
        for replay in self._replays:
            filename = os.path.join(self._replays_path, replay)
            to_decode = Replay_file(filename)
            #all_stats.append({'name': replay, 'gameloop': 0 })
            self._all_stats.append(to_decode.decode_replay())
        #return self._all_stats
    
    def export_stats_to_xlsx(self):
        self.replay_stats()
        
        self._df = pd.DataFrame(columns = ['gameloop', 'name'])
        for item in self._all_stats:
            app = pd.DataFrame(item, columns = ['gameloop', 'name'])
            self._df = self._df.append(app)

        writer = pd.ExcelWriter('death_stats.xlsx')
        self._df.to_excel(writer,'Sheet1')
        writer.save()
        return self._df
    
    @property
    def stats(self):
        if self._all_stats == []:
            self.replay_stats()
        else:
            pass
        return self._all_stats
            
   

class Replay_file(object):
    
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
        module_name = 'protocol{}.py'.format(build_number) #heroprotocol27.
        
        
        protocol = import_heroprotocol(module_name)        
            
            
            
        
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