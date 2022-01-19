# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 12:20:29 2020

@author: knutankv
"""
import glob
import zipfile
path = 'C:/Users/knutankv/Downloads/**/*.zip'

myzips = glob.glob(path, recursive=True)
bad_zips = []
for z in myzips:
  try:
    x = zipfile.ZipFile(z)
    x.close()
  except:
    bad_zips.append(z)
    continue

print(bad_zips)