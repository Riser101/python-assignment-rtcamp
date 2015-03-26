import subprocess as sp
import os

def hasPYMYSQL():
   try:
    sp.check_call(['pip3','--version'])
    sp.call(['sudo','pip3','install','PyMySQL'])
    return True
   except:
    sp.call(['sudo','apt-get','install','python3-pip'])
    sp.call(['sudo','pip3','install','PyMySQL'])
    return False
hasPYMYSQL()

def hasCEMENT():
 try:
  sp.call('pip3','install','cement')
  return True
 except:
  return False
hasCEMENT()
 
