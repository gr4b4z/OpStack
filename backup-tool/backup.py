#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(description='Backup toppl.')
parser.add_argument('action',choices=['export', 'import'],help='Action')
parser.add_argument('--instance-output', nargs='?', help='Instance output file',default='output_instance.csv')
parser.add_argument('--instance','-i', nargs='*', help='Specify instances that you want to export')

# parser.add_argument('--test','-t', nargs='?', help='Test run',default=False)
parser.add_argument('--pipe', action='store_true', help='Use this switch if you want to use pipe ex. echo "ext" | backup-tool.py ')
parser.add_argument('--check', action='store_true', help='Check ')

parser.add_argument('--username', nargs='*')
parser.add_argument('--pwd', nargs='*')
parser.add_argument('--project', nargs='*')
parser.add_argument('--url', nargs='*')
parser.add_argument('--config', nargs='*')

args = parser.parse_args()


from export_instance import export_metadata
from import_instances import Instance_importer
from model_manager import Model_manager
from progress_manager import Progress_manager
from volume_move import copy_volumes
import subprocess
import sys
import os
import logging
#logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.INFO,format='%(asctime)s %(message)s')




INSTANCE_FILE=args.instance_output
command = args.action 


if args.username != None:
    pass
elif args.config!=None or os.path.isfile('config.json'):
    import json
    with open(args.config if args.config != None else 'config.json', 'r') as f:
        cfg = json.load(f)
        args.username=cfg['username']
        args.pwd=cfg['password']
        args.url=cfg['url']
        args.project=cfg['project']
elif 'USERNAME' in os.environ:
    args.username=os.environ["USERNAME"]
    args.pwd=os.environ["PASSWORD"]
    args.url=os.environ["URL"]
    args.project=os.environ["PROJECT"]
    

if args.pipe:
    args.instance = sys.stdin.readlines()
    
if command == 'import':
    model=Model_manager(INSTANCE_FILE)
    (instances_kv,flavor_kv) = model.read_model()
    if args.instance!=None:
        instances_kv = {k: v for k, v in instances_kv.items() if k in args.instance}
    progress = Progress_manager()
    
    instances_to_process=progress.filter_by_progress(instances_kv)
    try:
        importer = Instance_importer(args.username, args.pwd,args.project,args.url)
        importer.prepare_instances(instances_to_process)
        if args.check == False:
            #importer.create_flavor(flavor_kv.values())
            importer.create_instances()
    except Exception as e: logging.exception(e)
    finally:
            progress.save_progress(instances_to_process)
elif command == 'export':
    logging.info("Exporting instance metadata")
    model=Model_manager(INSTANCE_FILE)
    (instances,flavors)=export_metadata(args.username, args.pwd,args.project,args.url,args.instance)
    #instances_to_export = Progress_manager().filter_by_exported(instances)
    instances_to_export=instances
    if args.check == False:
        copy_volumes(instances_to_export,args.username, args.pwd,args.project,args.url)
    model.save_model(instances)   