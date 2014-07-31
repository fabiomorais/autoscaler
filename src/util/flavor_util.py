
def get_data_flavor(flavor):
	return (str(flavor['id']), str(flavor['name']), (flavor['vcpus']), str(flavor['ram']), str(flavor['disk']))
