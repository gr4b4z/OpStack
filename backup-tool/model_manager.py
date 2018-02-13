from model import Flavor,Volume,Instance
import logging

class Model_manager:
    def __init__(self,instance_file='instances.csv'):
        self.INSTANCE_FILE=instance_file

    def save_model(self,instances_kv):
        logging.info('====================== Instances =====================')	
        instanceFile = open(self.INSTANCE_FILE,'w')
        for instance in instances_kv.values():
            for volume in instance.volumes:
                    fla = instance.flavor
                    row=('{},{},{},{},{},{},{},{},{},{}'.format(instance.host_name, instance.old_instance_id,fla.name,fla.cpu,fla.ram, volume.display_name, volume.mount_point, volume.is_bootable, volume.size,volume.old_volume_id)) 
                    instanceFile.write("{}\n".format(row))
                    logging.info(row)
        instanceFile.close()
        logging.info('Instances file : {0} '.format(self.INSTANCE_FILE))
        

    def read_model(self):
        import csv
        instances = {}
        flavors={}
        with open(self.INSTANCE_FILE, 'r') as csv_file:
            reader = csv.reader(line for line in csv_file)
            row_lines = list(reader)
            for e in row_lines:
                if e[1] not in instances:
                    if e[2] not in flavors:
                        flavors[e[2]]=Flavor(e[2],e[4],e[3])
                    instances[e[1]]=Instance(e[0],e[1],flavors[e[2]])
                vol = Volume(e[9],e[8],e[7]=='True',e[5],True)
                vol.setMountPoint(e[6])
                instances[e[1]].addVolume(vol)
            return (instances,flavors)