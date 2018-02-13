from model import Flavor,Volume,Instance

def export_metadata(user,passwd,project,url,instances = None):
	#global client
	from novaclient import client
	volume_list   = {}
	instance_list = {}
	flavor_list   = {}
	with client.Client('2', user,passwd,project,url) as nova:
		servers = nova.servers.list()
		flavors = nova.flavors.list()
		
		for fla in flavors:
			flavor_list[fla.id]=Flavor(fla.name,fla.ram,fla.vcpus)
			flavor_list[fla.id].flavor_old_id = fla.id
			
		for server in servers:
			if instances==None or instances != None and server.id in instances :
				instance_list[server.id]=Instance(server.name,server.id,flavor_list[server.flavor['id']])


	from cinderclient.v3 import client
	cinder = client.Client(user,passwd,project,url)
	volumes = cinder.volumes.list()
	for vol in volumes:
		for at in vol.attachments:
			if at['server_id'] in instance_list:
				s = instance_list[at['server_id']]
				volume=Volume(vol.id,vol.size,vol.bootable,vol.name,'yes')
				volume.setMountPoint(at['device'])
			        s.addVolume(volume)

	# if generate_output == False:
	return  (instance_list,flavor_list)	