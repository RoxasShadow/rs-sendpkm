#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    sendpkm.py is a module to send Pokémon at the fake GTS of Pokémon games.
    Tested only on ir-gts 0.43 <http://code.google.com/p/ir-gts/>
    Copyright (C) 2011  Giovanni 'Roxas Shadow' Capuano

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from pokehaxlib import *
from pkmlib import encode
from boxtoparty import makeparty
from gbatonds import makends
from sys import argv, exit
from platform import system
import os, random

def sendpkm():
    token = 'c9KcX1Cry3QKS2Ai7yxL6QiQGeBGeQKR'

    print 'Enter (or simply drag&drop) the path of the directory which contains the Pokémon:'
    path = raw_input().strip()
    if path.startswith('\'') or path.endswith('\''):
    	path = path.replace('\'', '')   	
    
    #Test
    path = os.path.normpath(path)
    if system() != 'Windows':
        path = path.replace('\\', '')
    	if not path.endswith('/'):
    		path = path+'/'
    else:
    	if not path.endswith('\\'):
    		path = path+'\\'
    #End

    while True:
        dirs = [] # Just you add/remove a file from your Pokémon directory, isn't a good thing killing the software :(
        for i in os.listdir(path):
            if i.lower().endswith('.pkm'):
                dirs.append(i)
        fileName = dirs[random.randint(0, len(dirs)-1)]
        pokeyman = path + fileName
        
        f = open(pokeyman, 'r')
        pkm = f.read()
        f.close()

	if pokeyman.lower().endswith('.pkm'):
            # Adding extra 100 bytes of party data
            if len(pkm) != 236 and len(pkm) != 136:
                print 'Invalid filesize.'
                return
            if len(pkm) == 136:
                print 'PC-Boxed Pokemon! Adding party data...',
                pkm = makeparty(pkm)
                print 'done.'
                
            print 'Encoding!'
            bin = encode(pkm)
        elif pokeyman.lower().endswith('.3gpkm'):
            print 'Converting GBA file to NDS format...',
            f = open(pokeyman, 'r')
            pkm = f.read()
            f.close()

            if len(pkm) != 80 and len(pkm) != 100:
                print 'Invalid filesize.'
                return
            pkm = makends(pkm)
            print 'done.'

            print 'Encoding!'
            bin = encode(pkm)
        else:
            print 'Filename must end in .pkm or .3gpkm'
            return

        # Adding GTS data to end of file
        bin += pkm[0x08:0x0a] # id
        if ord(pkm[0x40]) & 0x04: bin += '\x03' # Gender
        else: bin += chr((ord(pkm[0x40]) & 2) + 1)
        bin += pkm[0x8c] # Level
        bin += '\x01\x00\x03\x00\x00\x00\x00\x00' # Requesting bulba, either, any
        bin += '\x00' * 20 # Timestamps and PID
        bin += pkm[0x68:0x78] # OT Name
        bin += pkm[0x0c:0x0e] # OT ID
        bin += '\xDB\x02' # Country, City
        bin += '\x46\x00\x07\x02' # Sprite, Exchanged (?), Version, Lang

        sent = False
        delete = False
        print 'Ready to send; you can now enter the GTS...'
        while not sent:
            sock, req = getReq()
            a = req.action
            if len(req.getvars) == 1:
                sendResp(sock, token)
            elif a == 'info':
                sendResp(sock, '\x01\x00')
                print 'Connection Established.'
            elif a == 'setProfile': sendResp(sock, '\x00' * 8)
            elif a == 'post': sendResp(sock, '\x0c\x00')
            elif a == 'search': sendResp(sock, '')
            elif a == 'result': sendResp(sock, bin)
            elif a == 'delete':
                sendResp(sock, '\x01\x00')
                sent = True

        print fileName+' sent successfully.'
