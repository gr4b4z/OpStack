#!/usr/bin/python
import csv
import os
import subprocess
import sys
import logging
from model import Flavor,Volume,Instance
class Instance_importer:

    def __init__(self,user,passwd,project,url):
        self.user=user
        self.passwd=passwd
        self.project=project
        self.url=url
        self.flavor_list = {}
        self.instances_to_import=[]

    def create_flavor(self,new_flavors):
        
        with client.Client('2', self.user,self.passwd,self.project,self.url) as nova:
            flavors = nova.flavors.list()
            localByName={}
            for fla in flavors:
                new_flavor = Flavor(fla.name,fla.ram,fla.vcpus)
                self.flavor_list[fla.id] = new_flavor
                localByName[fla.name] = new_flavor
            
            for fla in new_flavors:
                if fla.name not in localByName:
                    new_flavor=nova.flavors.create(fla.name,fla.memory,fla.cpu,100) 
                    self.flavor_list[new_flavor.id]=new_flavor

    def processInstance(self, inst ):
        if inst.new_instance_id==None:
        # inst.new_instance_id = subprocess.check_output(['bash','-c', "./create_instance.sh {} {} {}".format(inst.flavor_id,inst.volumes[0].new_volume_id,inst.host_name)]).rstrip()
            inst.new_instance_id=subprocess.check_output(['bash','-c', "openstack server create --flavor {} --volume {} --security-group test --key-name cloud --nic net-id=a8b93582-2589-4a52-a2a5-862241eb3c8a {} -f value -c id".format(inst.flavor_id,vol.new_volume_id,inst.host_name)])
            subprocess.call(['sleep','5'])
            floatIP=subprocess.check_output(['bash','-c', "openstack floating ip list -f value | grep None | awk 'NR==1 {print {}}".format(inst.volumes[0].new_volume_id)])
            subprocess.call(['bash','-c', "openstack server add floating ip {} {}".format(instId,floatIP )])

            for vol in inst.volumes[1:]:
                logging.info('Attaching volume {}'.format(vol.mount_point))
                subprocess.check_output(['bash','-c', "openstack server add volume {} {}".format(inst.new_instance_id,vol.new_volume_id)])
        return inst

    def processVolume(self,vol):
        if vol.new_volume_id==None:
            if os.path.isfile('volumes/volume-{}.vmdk'.format(vol.old_volume_id)):
                logging.info("Creating Volume")
                vol.new_volume_id = subprocess.check_output(['bash','-c', "openstack volume create --size {} {} -c id -f value".format(vol.size,vol.display_name)]).rstrip()
                subprocess.call(["sleep", "5"])
                subprocess.call(["rbd","rm","volumes/volume-{}".format(vol.new_volume_id)])
                subprocess.call(["qemu-img","convert","-p","-f","vmdk","-O","raw","./volumes/volume-{}.vmdk".format(vol.old_volume_id),"./volumes/volume-{}.raw".format(vol.old_volume_id)])
                subprocess.call(["rbd","import","--image-format","2","./volumes/volume-{}.raw".format(vol.old_volume_id),"volumes/volume-{}".format(vol.new_volume_id)])
                subprocess.call(["rm", "./volumes/volume-{}.raw".format(vol.old_volume_id)])

                if vol.is_bootable:
                    logging.info('Setting {} as bootable'.format(vol.new_volume_id))
                    subprocess.check_output(['bash','-c', "cinder set-bootable {} True".format(vol.new_volume_id)])
            else:
                logging.info("ignoring volume, it doesn't exists on disk")
        return vol

    def create_instances(self):
        total=len(self.instances_to_import)
        i=0
        if total == 0:
            logging.info('# Nothing to import')

        for instance in self.instances_to_import:
            i=i+1
            logging.info('# Analyzing {}/{}'.format(i,total))
            logging.info(instance)
            for volume in instance.volumes:
                logging.info("   {}".format(volume))
               # self.processVolume(volume)
            #self.processInstance(instance)

    def prepare_instances(self,instances):
        all_instances = instances.values()
        goodInstances = []
        instancesWithMissingDisc = []
        wrongRootVolume=[]
    
        for instance in all_instances:
            exists = True
            existing_volumes=[]
            has_root_volume=False
            missing_volumes=[]
            for volume in instance.volumes:
                if os.path.isfile('volumes/volume-{}.vmdk'.format(volume.old_volume_id)):
                    exists=exists & True
                    existing_volumes.append(volume)
                    has_root_volume=has_root_volume or (volume.mount_point=='/dev/vda')
                else:
                    missing_volumes.append(volume.mount_point)
                    exists=exists & False
            if exists:
                logging.info('Complete VM {}'.format(instance.host_name))
                goodInstances.append(instance)
            elif has_root_volume:
                logging.info('Not Complete VM {}- Root volume exists'.format(instance.host_name))
                for p in missing_volumes: logging.info('   Missing volume {}'.format(p)) 
                instance.addVolumes(existing_volumes)
                instancesWithMissingDisc.append(instance)
            else:
                logging.info('Wrong VM {} - No volume'.format(instance.host_name))
                for p in missing_volumes: logging.info('   Missing volume {}'.format(p))
                wrongRootVolume.append(instance.host_name)
                
        self.instances_to_import=goodInstances + instancesWithMissingDisc	
        logging.info('-------------------------------')	
        logging.info('Good Instances              :{}'.format(len(goodInstances)))
        logging.info('Instances with missing disk :{}'.format(len(instancesWithMissingDisc)))
        logging.info('Instances with missing root :{}'.format(len(wrongRootVolume)))  
        