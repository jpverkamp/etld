#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

# Paths for the data file this module needs.
REMOTE_FILE = 'https://mxr.mozilla.org/mozilla-central/source/netwerk/dns/effective_tld_names.dat?raw=1'
LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'effective_tld_names.dat')

# Three sets of possible TLDs:
NORMAL_TLDS = set()
WILDCARD_TLDS = set()
SPECIAL_TLDS = set()

# Verify that an effective TLD file exists. If not, download it.
if not os.path.exists(LOCAL_FILE):
    urlretrieve(REMOTE_FILE, LOCAL_FILE)

# Load the effective TLD file
with open(LOCAL_FILE) as fin:
    for line in fin:
        if not line or line.startswith('//'):
            continue
        
        line = line.strip()
        
        if line.startswith('*'):
            WILDCARD_TLDS.add(line[2:])
        elif line.startswith('!'):
            SPECIAL_TLDS.add(line[1:])
        else:
            NORMAL_TLDS.add(line)

def split(hostname):
    """
    Split a hostname into domain, and effective TLD (remove subdomains)
    
    Examples:
    example.com           => ('example', 'com')   # Test com TLD
    sub.example.com       => ('example', 'com')
    sub.dub.example.com   => ('example', 'com')
    example.co.uk         => ('example', 'co.uk') # Test *.uk eTLD
    sub.example.co.uk     => ('example', 'co.uk')
    sub.dub.example.co.uk => ('example', 'co.uk')
    bl.uk                 => ('bl', 'uk')         # Exception to the normal *.uk 
    example.frog          => None                 # Return None on invalid TLDs
    """
    
    # Check TLDs left to right (sub.example.co.uk is sub.., example.., co.., uk..)
    parts = hostname.strip('.').split('.')
    tld = None
    for i in range(len(parts)):
        prev_tld = tld
        tld = '.'.join(parts[i:])
        
        # One step further if we have a special TLD
        if tld in SPECIAL_TLDS:
            return (parts[i], '.'.join(parts[i+1:]))
        
        # Process normal TLDs
        elif i >= 1 and tld in NORMAL_TLDS:
            return (parts[i-1], tld)
        
        # Process wildcard TLDs
        elif i >= 2 and tld in WILDCARD_TLDS and not prev_tld in SPECIAL_TLDS:
            return (parts[i-2], prev_tld)
        
    # No matching TLDs
    return None
        
if __name__ == '__main__':
    for query in sys.argv[1:]:
        print('{} => {}'.format(query, split(query)))
