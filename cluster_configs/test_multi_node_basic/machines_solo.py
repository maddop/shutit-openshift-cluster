machines = {}
machines.update({'master1':{
	'fqdn':'master1.vagrant.test',
	'is_certificate_server':False,
	'is_etcd':True,
	'is_first_etcd':False,
	'is_first_master':True,
	'is_lb':False,
	'is_master':True,
	'is_node':True,
	'region':'NA'
}})
machines.update({'master2':{
	'fqdn':'master2.vagrant.test',
	'is_certificate_server':False,
	'is_etcd':True,
	'is_first_etcd':False,
	'is_first_master':False,
	'is_lb':False,
	'is_master':True,
	'is_node':True,
	'region':'NA'
}})
machines.update({'master3':{
	'fqdn':'master3.vagrant.test',
	'is_certificate_server':False,
	'is_etcd':True,
	'is_first_etcd':False,
	'is_first_master':False,
	'is_lb':False,
	'is_master':True,
	'is_node':True,
	'region':'NA'
}})
machines.update({'node1':{
	'fqdn':'node1.vagrant.test',
	'is_certificate_server':False,
	'is_etcd':False,
	'is_first_etcd':False,
	'is_first_master':False,
	'is_lb':False,
	'is_master':False,
	'is_node':True,
	'region':'user'
}})
machines.update({'node2':{
	'fqdn':'node2.vagrant.test',
	'is_certificate_server':False,
	'is_etcd':False,
	'is_first_etcd':False,
	'is_first_master':False,
	'is_lb':False,
	'is_master':False,
	'is_node':True,
	'region':'infra'
}})
