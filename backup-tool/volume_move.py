from __future__ import print_function # needs to be first statement in file
import subprocess
from novaclient import client
import os
import time
import logging


def copy_volumes(instances,user,passwd,project,url):
    total=len(instances)
    i=0

    
    with client.Client('2', user,passwd,project,url) as nova:
        
        for inst in instances.values():
            i+=1
            vm=nova.servers.get(inst.old_instance_id)
            vm_status=str(vm.status)
            logging.info(vm_status)
            logging.info("Instance status {}: {}".format(inst.host_name,vm_status))
            if vm_status=='ACTIVE':
                logging.info("Stopping instance {} {}/{}".format(inst.host_name,i,total))
                timeout = 30
                vm.stop()
                while str(nova.servers.get(inst.old_instance_id).status)=='ACTIVE' and timeout>0:
                    time.sleep(1)
                    timeout-=1
                if timeout==0:
                    logging.info("Unable to stop VM {} {}/{}".format(inst.host_name,i,total))
                    continue
            else:
                logging.info("Instance already stopped {}/{}".format(i,total))
            j=0
            logging.info(nova.servers.get(inst.old_instance_id).status)
            for vol in inst.volumes:
                j+=1
                logging.info("Processing volume {}/{}... " .format(j,len(inst.volumes))) 
                if os.path.isfile('volumes/volume-{}.vmdk'.format(vol.old_volume_id)):
                    logging.info("already exists.") 
                    continue
                logging.info("exporting.") 
                vol_id=vol.old_volume_id
                subprocess.call(["rbd","export","volumes/volume-{0}".format(vol_id),"./volumes/volume-{0}.raw".format(vol_id)])
                logging.info("Converting")
                subprocess.call(["qemu-img","convert","-p","-f","raw","-O","vmdk","./volumes/volume-{}.raw".format(vol_id),"./volumes/volume-{}.vmdk".format(vol_id)])
                subprocess.call(["rm", "./volumes/volume-{}.raw".format(vol.old_volume_id)])
            
            if vm_status=='ACTIVE' and str(nova.servers.get(inst.old_instance_id).status)!='ACTIVE':
                logging.info(vm.status)
                vm.start()
                time.sleep(5)
            logging.info("Instance done")