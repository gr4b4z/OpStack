from model import Flavor,Volume,Instance
import csv
import os


class Progress_manager:
    def __init__(self,instance_file='status-instances.csv',vol_file='status-volumes.csv'):
        self.VOL_STATUS_FILE=vol_file
        self.INSTANCE_STATUS_FILE=instance_file

    def save_progress(self,all_instances_kv):
        instanceFile = open(self.INSTANCE_STATUS_FILE,'w')
        volumeFile = open(self.VOL_STATUS_FILE,'w')
        for instance in all_instances_kv.values():
            if instance.new_instance_id!=None:
                instanceFile.write('{},{}\n'.format(instance.old_instance_id,instance.new_instance_id)) 
            for volume in instance.volumes:
                if volume.new_volume_id!=None:
                    volumeFile.write('{},{}\n'.format(volume.old_volume_id,volume.new_volume_id)) 
        volumeFile.close()
        instanceFile.close()

    def read_progress(self):
        global csv
        global os
        instances = {}
        volumes = {}
        if os.path.isfile(self.INSTANCE_STATUS_FILE):
            with open(self.INSTANCE_STATUS_FILE, 'r') as csv_file:
                reader = csv.reader(line for line in csv_file)
                instance_status = list(reader)
                for ints in instance_status:
                    instances[ints[0]].new_instance_id = ints[1]

        if os.path.isfile(self.VOL_STATUS_FILE):
            with open(self.VOL_STATUS_FILE, 'r') as csv_file:
                reader = csv.reader(line for line in csv_file)
                volume_status = list(reader)
                for vol in volume_status:
                    volumes[vol[0]].new_volume_id = vol[1]
        return (instances,volumes)

    def filter_by_progress(self,all_instances):
        (inst_status,vol_status) = self.read_progress()
        for inst in all_instances.values():
            print inst
            for vol in inst.volumes:
                if  vol.old_volume_id in vol_status:
                    vol.new_volume_id = vol_status[vol.old_volume_id]
            if inst.old_instance_id in inst_status:
                inst.new_instance_id = inst_status[inst.old_instance_id]
        return all_instances

    def filter_by_exported(self,instances_kv):
        import os
        instances_to_export={}
        for inst in instances_kv.values():
            volumes_not_ready = len(inst.volumes)
            for vol in inst.volumes:
                if os.path.isfile('volumes/volume-{}.vmdk'.format(vol.old_volume_id)):
                    volumes_not_ready-=1
            if volumes_not_ready!=0:
                instances_to_export[inst.old_instance_id]=inst
        return instances_to_export