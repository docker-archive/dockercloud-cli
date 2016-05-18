# -*- coding: utf-8 -*-
import StringIO
import __builtin__
import unittest

import mock

import dockercloudcli
from dockercloudcli.commands import *


class ServiceCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.start')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.create')
    def test_service_create(self, mock_create, mock_save, mock_start):
        exposed_ports = [800, 222]
        published_ports = ['80:80/tcp', '22:22']
        ports = utils.parse_published_ports(published_ports)
        ports.extend(utils.parse_exposed_ports(exposed_ports))
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        service_create('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                       exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                       'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None, False, "host", "host")

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None, net="host", pid="host")
        mock_save.assert_called()
        mock_start.assert_not_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Service.start')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.create')
    def test_service_create_exposing_publishing_same_port(self, mock_create, mock_save, mock_start):
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        ports = [{'inner_port': '80', 'outer_port': '800', 'protocol': 'tcp', 'published': True}]
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None, False, "host", "host")

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None, net="host", pid="host")
        mock_save.assert_called()
        mock_start.assert_not_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.create', side_effect=dockercloud.ApiError)
    def test_service_create_with_exception(self, mock_create, mock_exit):
        exposed_ports = ['80', '22']
        published_ports = ['80:80/tcp', '22:22']
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service_create('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                       exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                       'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None, False, "host", "host")

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.get_all_attributes')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_inspect(self, mock_fetch_remote_service, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = uuid
        mock_fetch_remote_service.return_value = service
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        service_inspect(['test_id'])

        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_inspect_with_exception(self, mock_fetch_remote_service, mock_exit):
        service = dockercloudcli.commands.dockercloud.Service()
        mock_fetch_remote_service.return_value = service
        service_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServicePsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        service1 = dockercloudcli.commands.dockercloud.Service()
        service1.current_num_containers = 3
        service1.name = 'SERVICE1'
        service1.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        service1.image_name = 'test/service1'
        service1.web_public_dns = 'service1.io'
        service1.state = 'Running'
        service1.deployed_datetime = ''
        service1.synchronized = True
        service1.public_dns = "www.myhello1service.com"
        service1.stack = "/resource_uri/service1"
        service2 = dockercloudcli.commands.dockercloud.Service()
        service2.current_num_containers = 2
        service2.name = 'SERVICE2'
        service2.uuid = '8B4CFE51-03BB-42D6-825E-3B533888D8CD'
        service2.image_name = 'test/service2'
        service2.web_public_dns = 'service2.io'
        service2.state = 'Stopped'
        service2.deployed_datetime = ''
        service2.synchronized = True
        service2.public_dns = "www.myhello2service.com"
        service2.stack = "/resource_uri/service2"
        self.servicelist = [service1, service2]
        stack1 = dockercloudcli.commands.dockercloud.Stack()
        stack1.resource_uri = "/resource_uri/service1"
        stack1.name = "service1"
        stack2 = dockercloudcli.commands.dockercloud.Stack()
        stack2.resource_uri = "/resource_uri/service2"
        stack2.name = "service2"
        self.stacklist = [stack1, stack2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Stack.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list')
    def test_service_ps(self, mock_list, mock_stack):
        output = u'''NAME      UUID      STATUS       #CONTAINERS  IMAGE          DEPLOYED    PUBLIC DNS               STACK
SERVICE1  7A4CFE51  \u25b6 Running              3  test/service1              www.myhello1service.com  service1
SERVICE2  8B4CFE51  \u25fc Stopped              2  test/service2              www.myhello2service.com  service2'''
        mock_list.return_value = self.servicelist
        mock_stack.return_value = self.stacklist
        service_ps(False, 'Running', None)

        mock_list.assert_called_with(state='Running', stack=None)
        self.buf.getvalue().strip()
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Stack.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list')
    def test_service_ps_quiet(self, mock_list, mock_stack):
        output = '''7A4CFE51-03BB-42D6-825E-3B533888D8CD
8B4CFE51-03BB-42D6-825E-3B533888D8CD'''
        mock_stack.return_value = self.stacklist
        mock_list.return_value = self.servicelist
        service_ps(True, None, None)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list', side_effect=dockercloud.ApiError)
    def test_service_ps_with_exception(self, mock_list, mock_exit):
        service_ps(False, None, None)
        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)

    @mock.patch('dockercloudcli.commands.dockercloud.Stack.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list')
    def test_service_ps_unsync(self, mock_list, mock_stack):
        output = u'''NAME      UUID      STATUS          #CONTAINERS  IMAGE          DEPLOYED    PUBLIC DNS               STACK
SERVICE1  7A4CFE51  \u25b6 Running(*)              3  test/service1              www.myhello1service.com  service1
SERVICE2  8B4CFE51  \u25fc Stopped                 2  test/service2              www.myhello2service.com  service2

(*) Please note that this service needs to be redeployed to have its configuration changes applied'''
        self.servicelist[0].synchronized = False
        mock_stack.return_value = self.stacklist
        mock_list.return_value = self.servicelist
        service_ps(False, 'Running', None)

        mock_list.assert_called_with(state='Running', stack=None)
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)


class ServiceRunTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.start')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.create')
    def test_service_run(self, mock_create, mock_save, mock_start):
        exposed_ports = [800, 222]
        published_ports = ['80:80/tcp', '22:22']
        ports = utils.parse_published_ports(published_ports)
        ports.extend(utils.parse_exposed_ports(exposed_ports))
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        mock_start.return_value = True
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None, False, "host", "host")

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None, net="host", pid="host")
        mock_save.assert_called()
        mock_start.assert_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Service.start')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.create')
    def test_service_run_exposing_publishing_same_port(self, mock_create, mock_save, mock_start):
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        ports = [{'inner_port': '80', 'outer_port': '800', 'protocol': 'tcp', 'published': True}]
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = service
        mock_start.return_value = True
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None, False, "host", "host")

        mock_create.assert_called_with(image='imagename', name='containername', cpu_shares=1,
                                       memory='256M', privileged=True,
                                       target_num_containers=3, run_command='-d',
                                       entrypoint='/bin/mysql', container_ports=ports,
                                       container_envvars=utils.parse_envvars(container_envvars, []),
                                       linked_to_service=utils.parse_links(linked_to_service, 'to_service'),
                                       autorestart='OFF', autodestroy='OFF', autoredeploy='OFF',
                                       roles='poweruser', sequential_deployment=True, tags=[], bindings=[],
                                       deployment_strategy=None, net="host", pid="host")
        mock_save.assert_called()
        mock_start.assert_called()
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.create', side_effect=dockercloud.ApiError)
    def test_service_run_with_exception(self, mock_create, mock_exit):
        exposed_ports = ['80', '22']
        published_ports = ['80:80/tcp', '22:22']
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service_run('imagename', 'containername', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, None, None, None, False, "host", "host")

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceScaleTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_scale(self, mock_fetch_remote_service, mock_save):
        service = mock.MagicMock(spec=dockercloudcli.commands.dockercloud.Service)
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        service.is_dirty.side_effect = False
        mock_fetch_remote_service.return_value = service
        service_scale(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], 3, False)

        mock_save.assert_called()
        self.assertEqual(3, service.target_num_containers)
        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_scale_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_scale(['test_id'], 3, False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceSetTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_set(self, mock_fetch_remote_service, mock_save):
        service = dockercloudcli.commands.dockercloud.Service()
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        ports = [{'inner_port': '80', 'outer_port': '800', 'protocol': 'tcp', 'published': True}]
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'

        mock_fetch_remote_service.return_value = service
        service_set([service.uuid], 'imagename', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', False, 'poweruser', True, False, None, None, None, False, "host", "host")

        mock_save.assert_called()
        self.assertEqual('7A4CFE51-03BB-42D6-825E-3B533888D8CD\n'
                         'Service must be redeployed to have its configuration changes applied.\n'
                         'To redeploy execute: $ docker-cloud service redeploy 7A4CFE51-03BB-42D6-825E-3B533888D8CD',
                         self.buf.getvalue().strip())
        self.assertEqual(1, service.cpu_shares)
        self.assertEqual('256M', service.memory)
        self.assertEqual(True, service.privileged)
        self.assertEqual(3, service.target_num_containers)
        self.assertEqual('-d', service.run_command)
        self.assertEqual('/bin/mysql', service.entrypoint)
        self.assertEqual(ports, service.container_ports)
        self.assertEqual(utils.parse_envvars(container_envvars, []), service.container_envvars)
        self.assertEqual(utils.parse_links(linked_to_service, 'to_service'), service.linked_to_service)
        self.assertEqual('OFF', service.autorestart)
        self.assertEqual('OFF', service.autodestroy)
        self.assertEqual(False, service.autoredeploy)
        self.assertEqual('poweruser', service.roles)
        self.assertEqual(True, service.sequential_deployment)
        self.assertEqual("host", service.net)
        self.assertEqual("host", service.pid)
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_set_with_exception(self, mock_fetch_remote_service, mock_exit):
        service = dockercloudcli.commands.dockercloud.Service()
        exposed_ports = [80]
        published_ports = ['800:80/tcp']
        container_envvars = ['MYSQL_ADMIN=admin', 'MYSQL_PASS=password']
        linked_to_service = ['mysql:mysql', 'redis:redis']

        mock_fetch_remote_service.return_value = service
        service_set(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], 'imagename', 1, '256M', True, 3, '-d', '/bin/mysql',
                    exposed_ports, published_ports, container_envvars, [], '', linked_to_service,
                    'OFF', 'OFF', 'OFF', 'poweruser', True, False, None, None, None, False, "host", "host")

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceStartTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.start')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_start(self, mock_fetch_remote_service, mock_start):
        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_start.return_value = True
        service_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_start_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceStopTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.stop')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_stop(self, mock_fetch_remote_service, mock_stop):
        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_stop.return_value = True
        service_stop(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_stop_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceTerminateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.delete')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_teminate(self, mock_fetch_remote_service, mock_delete):
        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_delete.return_value = True
        service_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_terminate_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ServiceRedeployTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Service.redeploy')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service')
    def test_service_redeploy(self, mock_fetch_remote_service, mock_redeploy):
        service = dockercloudcli.commands.dockercloud.Service()
        service.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_service.return_value = service
        mock_redeploy.return_value = True
        service_redeploy(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], True, False)

        self.assertEqual(service.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_service', side_effect=dockercloud.ApiError)
    def test_service_redeploy_with_exception(self, mock_fetch_remote_service, mock_exit):
        service_redeploy(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], True, False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Container.get_all_attributes')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container')
    def test_container_inspect(self, mock_fetch_remote_container, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        container = dockercloudcli.commands.dockercloud.Container()
        container.uuid = uuid
        mock_fetch_remote_container.return_value = container
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        container_inspect(['test_id'])

        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container', side_effect=dockercloud.ApiError)
    def test_container_inspect_with_exception(self, mock_fetch_remote_container, mock_exit):
        container = dockercloudcli.commands.dockercloud.Container()
        mock_fetch_remote_container.return_value = container
        container_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerPsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        container1 = dockercloudcli.commands.dockercloud.Container()
        container1.name = 'CONTAINER1'
        container1.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        container1.image_name = 'test/container1'
        container1.public_dns = 'container1.io'
        container1.state = 'Running'
        container1.deployed_datetime = ''
        container1.run_command = '/bin/bash'
        container1.container_ports = [{'protocol': 'tcp', 'inner_port': 8080, 'outer_port': 8080}]
        container1.exit_code = 1
        container1.service = 'container1_service_uri'
        container1.node = 'container1_node_uri'
        container2 = dockercloudcli.commands.dockercloud.Container()
        container2.name = 'CONTAINER2'
        container2.uuid = '8B4CFE51-03BB-42D6-825E-3B533888D8CD'
        container2.image_name = 'test/container2'
        container2.public_dns = 'container2.io'
        container2.state = 'Stopped'
        container2.deployed_datetime = ''
        container2.run_command = '/bin/sh'
        container2.container_ports = [{'protocol': 'tcp', 'inner_port': 3306, 'outer_port': 3307}]
        container2.exit_code = 0
        container2.service = 'container2_service_uri'
        container2.node = 'container2_node_uri'
        self.containerlist = [container1, container2]
        service1 = dockercloudcli.commands.dockercloud.Service()
        service1.resource_uri = 'container1_service_uri'
        service1.stack = 'container1_service_stack_uri'
        service2 = dockercloudcli.commands.dockercloud.Service()
        service2.resource_uri = 'container2_service_uri'
        service2.stack = 'container2_service_stack_uri'
        self.servicelist = [service1, service2]
        stack1 = dockercloudcli.commands.dockercloud.Stack()
        stack1.resource_uri = 'container1_service_stack_uri'
        stack1.name = 'service1'
        stack2 = dockercloudcli.commands.dockercloud.Stack()
        stack2.resource_uri = 'container2_service_stack_uri'
        stack2.name = 'service2'
        self.stacklist = [stack1, stack2]
        node1 = dockercloudcli.commands.dockercloud.Node()
        node1.resource_uri = 'container1_node_uri'
        node1.uuid = 'd20430ae-da6d-4c13-bc91-ab15cf0b973d'
        node2 = dockercloudcli.commands.dockercloud.Node()
        node2.resource_uri = 'container2_node_uri'
        node2.uuid = '445c3d27-0dd4-443c-ad51-ea7539083114'
        self.nodelist = [node1, node2]

    def tearDown(self):
        pass
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Node.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Stack.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Container.list')
    def test_container_ps_trunc(self, mock_list, mock_service, mock_stack, mock_node):
        output = u'''NAME        UUID      STATUS     IMAGE            RUN COMMAND      EXIT CODE  DEPLOYED    PORTS                 NODE      STACK
CONTAINER1  7A4CFE51  \u25b6 Running  test/container1  /bin/bash                1              container1.io:808...  d20430ae  service1
CONTAINER2  8B4CFE51  \u25fc Stopped  test/container2  /bin/sh                  0              container2.io:330...  445c3d27  service2'''
        mock_node.return_value = self.nodelist
        mock_stack.return_value = self.stacklist
        mock_service.return_value = self.servicelist
        mock_list.return_value = self.containerlist

        container_ps(False, 'Running', None, False)

        mock_list.assert_called_with(state='Running', service=None)
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Node.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Stack.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Container.list')
    def test_container_ps_notrunc(self, mock_list, mock_service, mock_stack, mock_node):
        output = u'''NAME        UUID                                  STATUS     IMAGE            RUN COMMAND      EXIT CODE  DEPLOYED    PORTS                         NODE                                  STACK
CONTAINER1  7A4CFE51-03BB-42D6-825E-3B533888D8CD  \u25b6 Running  test/container1  /bin/bash                1              container1.io:8080->8080/tcp  d20430ae-da6d-4c13-bc91-ab15cf0b973d  service1
CONTAINER2  8B4CFE51-03BB-42D6-825E-3B533888D8CD  \u25fc Stopped  test/container2  /bin/sh                  0              container2.io:3307->3306/tcp  445c3d27-0dd4-443c-ad51-ea7539083114  service2'''
        mock_node.return_value = self.nodelist
        mock_stack.return_value = self.stacklist
        mock_service.return_value = self.servicelist
        mock_list.return_value = self.containerlist
        container_ps(False, 'Running', None, True)

        mock_list.assert_called_with(state='Running', service=None)
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Node.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Stack.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Service.list')
    @mock.patch('dockercloudcli.commands.dockercloud.Container.list')
    def test_container_ps_quiet(self, mock_list, mock_service, mock_stack, mock_node):
        output = '''7A4CFE51-03BB-42D6-825E-3B533888D8CD
8B4CFE51-03BB-42D6-825E-3B533888D8CD'''
        mock_node.return_value = self.nodelist
        mock_stack.return_value = self.stacklist
        mock_service.return_value = self.servicelist
        mock_list.return_value = self.containerlist
        container_ps(True, None, None, False)
        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Container.list', side_effect=dockercloud.ApiError)
    def test_container_ps_with_exception(self, mock_list, mock_exit):
        container_ps(None, None, None, False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerStartTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Container.start')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container')
    def test_container_start(self, mock_fetch_remote_container, mock_start):
        container = dockercloudcli.commands.dockercloud.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_start.return_value = True
        container_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container', side_effect=dockercloud.ApiError)
    def test_container_start_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerStopTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Container.stop')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container')
    def test_container_stop(self, mock_fetch_remote_container, mock_stop):
        container = dockercloudcli.commands.dockercloud.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_stop.return_value = True
        container_stop(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container', side_effect=dockercloud.ApiError)
    def test_container_stop_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_start(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerTerminateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Container.delete')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container')
    def test_container_teminate(self, mock_fetch_remote_container, mock_delete):
        container = dockercloudcli.commands.dockercloud.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_delete.return_value = True
        container_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container', side_effect=dockercloud.ApiError)
    def test_container_terminate_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_terminate(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class ContainerRedeployTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Container.redeploy')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container')
    def test_container_redeploy(self, mock_fetch_remote_container, mock_redeploy):
        container = dockercloudcli.commands.dockercloud.Container()
        container.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_container.return_value = container
        mock_redeploy.return_value = True
        container_redeploy(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], True, False)

        self.assertEqual(container.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_container', side_effect=dockercloud.ApiError)
    def test_container_redeploy_with_exception(self, mock_fetch_remote_container, mock_exit):
        container_redeploy(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], True, False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class RepositoryListTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        repository1 = dockercloudcli.commands.dockercloud.Repository()
        repository1.name = 'r-staging.dockercloud.co/admin/tutum-sdk'
        repository1.in_use = False
        repository1.description = ''
        repository1.is_private_image = True
        repository1.build_source = True
        repository1.tags = ["1"]
        repository2 = dockercloudcli.commands.dockercloud.Repository()
        repository2.name = 'r-staging.dockercloud.co/admin/python-quickstart'
        repository2.description = ''
        repository2.in_use = False
        repository2.is_private_image = True
        repository2.build_source = True
        repository2.tags = ["2"]

        self.repositorylist = [repository1, repository2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Repository.list')
    def test_repository_list(self, mock_list):
        output = u'''NAME                                              IN_USE
r-staging.dockercloud.co/admin/tutum-sdk          no
r-staging.dockercloud.co/admin/python-quickstart  no'''
        mock_list.return_value = self.repositorylist
        repository_ls(False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Repository.list')
    def test_repository_list_quiet(self, mock_list):
        output = 'r-staging.dockercloud.co/admin/tutum-sdk\nr-staging.dockercloud.co/admin/python-quickstart'
        mock_list.return_value = self.repositorylist
        repository_ls(True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.list', side_effect=dockercloud.ApiError)
    def test_repository_list_with_exception(self, mock_fetch_remote_container, mock_exit):
        repository_ls(False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class RepositoryRegister(unittest.TestCase):
    def setUp(self):
        self.raw_input_holder = __builtin__.raw_input
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout
        __builtin__.raw_input = self.raw_input_holder

    @mock.patch('dockercloudcli.commands.dockercloud.Repository.save', return_value=True)
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.create')
    @mock.patch('dockercloudcli.commands.getpass.getpass', return_value='password')
    def test_register(self, mock_get_pass, mock_create, mock_save):
        output = '''Please input username and password of the registry:
repository_name'''
        __builtin__.raw_input = lambda _: 'username'  # set username
        repository = dockercloudcli.commands.dockercloud.Repository()
        repository.name = 'repository_name'
        mock_create.return_value = repository
        repository_register('repository', None, None)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.create', side_effect=dockercloud.ApiError)
    @mock.patch('dockercloudcli.commands.getpass.getpass', return_value='password')
    def test_register_with_exception(self, mock_get_pass, mock_create, mock_exit):
        __builtin__.raw_input = lambda _: 'username'  # set username
        repository_register('repository', None, None)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class RepositoryRmTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Repository.delete', return_value=True)
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.fetch')
    def test_repository_rm(self, mock_fetch, mock_delete):
        repository_rm(['repo1', 'repo2'])

        self.assertEqual('repo1\nrepo2', self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.delete', return_value=True)
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.fetch')
    def test_repository_rm_with_exception(self, mock_fetch, mock_delete, mock_exit):
        mock_fetch.side_effect = [dockercloudcli.commands.dockercloud.Repository(), dockercloud.ApiError]
        repository_rm(['repo1', 'repo2'])

        self.assertEqual('repo1', self.buf.getvalue().strip())
        self.buf.truncate(0)
        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class RepositoryUpdateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Repository.save', return_value=True)
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.fetch')
    def test_repository_update(self, mock_fetch, mock_save):
        repository = dockercloudcli.commands.dockercloud.Repository()
        repository.name = 'name'
        mock_fetch.return_value = repository
        mock_save.return_value = True
        repository_update(['repo'], 'username', 'password')
        self.assertEqual('username', repository.username)
        self.assertEqual('password', repository.password)
        self.assertEqual('name', self.buf.getvalue().strip())

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Repository.fetch')
    def test_repository_update_with_exception(self, mock_fetch, mock_exit):
        mock_fetch.side_effect = dockercloud.ApiError
        repository_update(['repo'], 'username', 'password')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeListTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        node1 = dockercloudcli.commands.dockercloud.Node()
        node1.uuid = '19303d01-3564-437b-ac54-e7f8d17003f6'
        node1.external_fqdn = '19303d01-tifayuki.node.dockercloud.io'
        node1.state = 'Deployed'
        node1.last_seen = None
        node1.node_cluster = '/api/infra/v1/nodecluster/b0374cc2-4003-4270-b131-25fc494ea2be/'
        node2 = dockercloudcli.commands.dockercloud.Node()
        node2.uuid = 'bd276db4-cd35-4311-8110-1c82885c33d2'
        node2.external_fqdn = 'bd276db4-tifayuki.node.dockercloud.io"'
        node2.state = 'Deploying'
        node2.last_seen = None
        node2.node_cluster = '/api/infra/v1/nodecluster/b0374cc2-4003-4270-b131-25fc494ea2be/'
        self.nodeklist = [node1, node2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.Node.list')
    def test_node_list(self, mock_list, mock_fetch):
        output = u'''UUID      FQDN                              LASTSEEN    STATUS       CLUSTER
19303d01  19303d01-tifayuki.node.dockercloud.io               ▶ Deployed   test_nodecluster
bd276db4  bd276db4-tifayuki.node.dockercloud.io"              ⚙ Deploying  test_nodecluster'''
        mock_list.return_value = self.nodeklist
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster.name = 'test_nodecluster'
        mock_fetch.return_value = nodecluster
        node_ls(quiet=False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.Node.list')
    def test_node_list(self, mock_list, mock_fetch):
        output = '''19303d01-3564-437b-ac54-e7f8d17003f6
bd276db4-cd35-4311-8110-1c82885c33d2'''
        mock_list.return_value = self.nodeklist
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster.name = 'test_nodecluster'
        mock_fetch.return_value = nodecluster
        node_ls(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Node.list', side_effect=dockercloud.ApiError)
    def test_node_list(self, mock_list, mock_exit):
        node_ls(False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Node.get_all_attributes')
    @mock.patch('dockercloudcli.commands.dockercloud.Node.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_node')
    def test_node_inspect(self, mock_fetch_remote_node, mock_fetch, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        node = dockercloudcli.commands.dockercloud.Node()
        node.uuid = uuid
        mock_fetch.return_value = node
        mock_fetch_remote_node.return_value = node
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        node_inspect(['test_id'])

        mock_fetch.assert_called_with(uuid)
        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_node', side_effect=dockercloud.ApiError)
    def test_node_inspect_with_exception(self, mock_fetch_remote_node, mock_exit):
        node = dockercloudcli.commands.dockercloud.Node()
        mock_fetch_remote_node.return_value = node
        node_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeRmTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Node.delete')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_node')
    def test_node_teminate(self, mock_fetch_remote_node, mock_delete):
        node = dockercloudcli.commands.dockercloud.Node()
        node.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_node.return_value = node
        mock_delete.return_value = True
        node_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(node.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_node', side_effect=dockercloud.ApiError)
    def test_node_terminate_with_exception(self, mock_fetch_remote_node, mock_exit):
        node_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterListTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        nodecluster1 = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster1.name = 'test_sfo'
        nodecluster1.uuid = 'b0374cc2-4003-4270-b131-25fc494ea2be'
        nodecluster1.region = '/api/infra/v1/region/digitalocean/sfo1/'
        nodecluster1.node_type = '/api/infra/v1/nodetype/digitalocean/512mb/'
        nodecluster1.deployed_datetime = None
        nodecluster1.state = 'Deployed'
        nodecluster1.current_num_nodes = 2
        nodecluster1.target_num_nodes = 2
        nodecluster2 = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster2.name = 'newyork3'
        nodecluster2.uuid = 'a4c1e712-ca26-4547-adb7-8da1057b964b'
        nodecluster2.region = '/api/infra/v1/region/digitalocean/nyc3/'
        nodecluster2.node_type = '/api/infra/v1/nodetype/digitalocean/512mb/'
        nodecluster2.deployed_datetime = None
        nodecluster2.state = 'Provisioning'
        nodecluster2.current_num_nodes = 1
        nodecluster2.target_num_nodes = 1
        self.nodeclusterlist = [nodecluster1, nodecluster2]

        region1 = dockercloudcli.commands.dockercloud.Region()
        region1.label = 'New York 3'
        region2 = dockercloudcli.commands.dockercloud.Region()
        region2.label = 'San Francisco 1'
        self.regionlist = [region1, region2]

        nodetype1 = dockercloudcli.commands.dockercloud.NodeType()
        nodetype1.label = '512MB'
        nodetype2 = dockercloudcli.commands.dockercloud.NodeType()
        nodetype2.label = '512MB'
        self.nodetypelist = [nodetype1, nodetype2]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Region.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.list')
    def test_clusternode_list(self, mock_list, mock_nodetype_fetch, mock_region_fetch):
        mock_list.return_value = self.nodeclusterlist
        mock_nodetype_fetch.side_effect = self.nodetypelist
        mock_region_fetch.side_effect = self.regionlist
        output = '''NAME      UUID      REGION           TYPE    DEPLOYED    STATUS          CURRENT#NODES    TARGET#NODES
test_sfo  b0374cc2  New York 3       512MB               Deployed                    2               2
newyork3  a4c1e712  San Francisco 1  512MB               Provisioning                1               1'''
        nodecluster_ls(quiet=False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Region.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.list')
    def test_clusternode_list_quiet(self, mock_list, mock_nodetype_fetch, mock_region_fetch):
        mock_list.return_value = self.nodeclusterlist
        mock_nodetype_fetch.side_effect = self.nodetypelist
        mock_region_fetch.side_effect = self.regionlist
        output = 'b0374cc2-4003-4270-b131-25fc494ea2be\na4c1e712-ca26-4547-adb7-8da1057b964b'
        nodecluster_ls(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.list', side_effect=dockercloud.ApiError)
    def test_clusternode_list_with_excepiton(self, mock_list, mock_exit):
        nodecluster_ls(quiet=True)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterInspectTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.get_all_attributes')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.fetch')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_nodecluster')
    def test_nodecluster_inspect(self, mock_fetch_remote_node_cluster, mock_fetch, mock_get_all_attributes):
        output = '''{
  "key": [
    {
      "name": "test",
      "id": "1"
    }
  ]
}'''
        uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster.uuid = uuid
        mock_fetch.return_value = nodecluster
        mock_fetch_remote_node_cluster.return_value = nodecluster
        mock_get_all_attributes.return_value = {'key': [{'name': 'test', 'id': '1'}]}
        nodecluster_inspect(['test_id'])

        mock_fetch.assert_called_with(uuid)
        self.assertEqual(' '.join(output.split()), ' '.join(self.buf.getvalue().strip().split()))
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_nodecluster', side_effect=dockercloud.ApiError)
    def test_nodecluster_inspect_with_exception(self, mock_fetch_remote_nodecluster, mock_exit):
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        mock_fetch_remote_nodecluster.return_value = nodecluster
        nodecluster_inspect(['test_id', 'test_id2'])

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterRmTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.delete')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_nodecluster')
    def test_nodecluster_rm(self, mock_fetch_remote_nodecluster, mock_delete):
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_nodecluster.return_value = nodecluster
        mock_delete.return_value = True
        nodecluster_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        self.assertEqual(nodecluster.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_nodecluster', side_effect=dockercloud.ApiError)
    def test_nodecluster_rm_with_exception(self, mock_fetch_remote_nodecluster, mock_exit):
        nodecluster_rm(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterScaleTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.save')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_nodecluster')
    def test_nodecluster_scale(self, mock_fetch_remote_nodecluster, mock_save):
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_fetch_remote_nodecluster.return_value = nodecluster
        nodecluster_scale(['7A4CFE51-03BB-42D6-825E-3B533888D8CD'], 3, False)

        mock_save.assert_called()
        self.assertEqual(3, nodecluster.target_num_nodes)
        self.assertEqual(nodecluster.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Utils.fetch_remote_nodecluster', side_effect=dockercloud.ApiError)
    def test_nodecluster_scale_with_exception(self, mock_fetch_remote_nodecluster, mock_exit):
        nodecluster_scale(['test_id'], 3, False)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterShowProviderTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

        provider = dockercloudcli.commands.dockercloud.Provider()
        provider.name = 'digitalocean'
        provider.label = 'Digital Ocean'
        provider.regions = [
            "/api/infra/v1/region/digitalocean/ams1/",
            "/api/infra/v1/region/digitalocean/ams2/",
            "/api/infra/v1/region/digitalocean/ams3/",
            "/api/infra/v1/region/digitalocean/lon1/",
            "/api/infra/v1/region/digitalocean/nyc1/",
            "/api/infra/v1/region/digitalocean/nyc2/",
            "/api/infra/v1/region/digitalocean/nyc3/",
            "/api/infra/v1/region/digitalocean/sfo1/",
            "/api/infra/v1/region/digitalocean/sgp1/"
        ]
        self.providerlist = [provider]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Provider.list')
    def test_nodecluster_show_providers(self, mock_list):
        output = '''NAME          LABEL
digitalocean  Digital Ocean'''
        mock_list.return_value = self.providerlist
        nodecluster_show_providers(quiet=False)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Provider.list')
    def test_nodecluster_show_providers_quiet(self, mock_list):
        output = 'digitalocean'
        mock_list.return_value = self.providerlist
        nodecluster_show_providers(quiet=True)

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Provider.list', side_effect=dockercloud.ApiError)
    def test_nodecluster_show_providers_with_exception(self, mock_list, mock_exit):
        nodecluster_show_providers(quiet=True)

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterShowRegionsTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        region1 = dockercloudcli.commands.dockercloud.Region()
        region1.name = 'ams1'
        region1.label = 'Amsterdam 1'
        region1.resource_uri = '/api/infra/v1/region/digitalocean/ams1/'
        region1.node_types = ["/api/infra/v1/nodetype/digitalocean/512mb/",
                              "/api/infra/v1/nodetype/digitalocean/1gb/",
                              "/api/infra/v1/nodetype/digitalocean/2gb/",
                              "/api/infra/v1/nodetype/digitalocean/4gb/",
                              "/api/infra/v1/nodetype/digitalocean/8gb/",
                              "/api/infra/v1/nodetype/digitalocean/16gb/"]
        region2 = dockercloudcli.commands.dockercloud.Region()
        region2.name = 'sfo1'
        region2.label = 'San Francisco 1'
        region2.resource_uri = '/api/infra/v1/region/digitalocean/sfo1/'
        region2.node_types = ["/api/infra/v1/nodetype/digitalocean/512mb/",
                              "/api/infra/v1/nodetype/digitalocean/1gb/",
                              "/api/infra/v1/nodetype/digitalocean/2gb/",
                              "/api/infra/v1/nodetype/digitalocean/4gb/",
                              "/api/infra/v1/nodetype/digitalocean/8gb/",
                              "/api/infra/v1/nodetype/digitalocean/16gb/",
                              "/api/infra/v1/nodetype/digitalocean/32gb/",
                              "/api/infra/v1/nodetype/digitalocean/48gb/",
                              "/api/infra/v1/nodetype/digitalocean/64gb/"]
        region3 = dockercloudcli.commands.dockercloud.Region()
        region3.name = 'jap1'
        region3.label = 'Japan 1'
        region3.resource_uri = '/api/infra/v1/region/aws/jap1/'
        region3.node_types = ["/api/infra/v1/nodetype/aws/512mb/",
                              "/api/infra/v1/nodetype/aws/1gb/",
                              "/api/infra/v1/nodetype/aws/2gb/",
                              "/api/infra/v1/nodetype/aws/4gb/",
                              "/api/infra/v1/nodetype/aws/8gb/"]
        self.regionlist = [region1, region2, region3]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.Region.list')
    def test_nodecluster_show_regions(self, mock_list):
        output = '''NAME    LABEL            PROVIDER
ams1    Amsterdam 1      digitalocean
sfo1    San Francisco 1  digitalocean
jap1    Japan 1          aws'''
        mock_list.return_value = self.regionlist
        nodecluster_show_regions('')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.Region.list')
    def test_nodecluster_show_regions_with_filter(self, mock_list):
        output = '''NAME    LABEL            PROVIDER
ams1    Amsterdam 1      digitalocean
sfo1    San Francisco 1  digitalocean'''
        mock_list.return_value = self.regionlist
        nodecluster_show_regions('digitalocean')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.Region.list', side_effect=dockercloud.ApiError)
    def test_nodecluster_show_regions_with_exception(self, mock_list, mock_exit):
        nodecluster_show_regions('')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterShowTypesTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()
        nodetype1 = dockercloudcli.commands.dockercloud.NodeType()
        nodetype1.name = '512mb'
        nodetype1.label = '512MB'
        nodetype1.resource_uri = '/api/infra/v1/nodetype/digitalocean/512mb/'
        nodetype1.regions = ["/api/infra/v1/region/digitalocean/ams1/",
                             "/api/infra/v1/region/digitalocean/sfo1/",
                             "/api/infra/v1/region/digitalocean/nyc2/",
                             "/api/infra/v1/region/digitalocean/ams2/",
                             "/api/infra/v1/region/digitalocean/sgp1/",
                             "/api/infra/v1/region/digitalocean/lon1/",
                             "/api/infra/v1/region/digitalocean/nyc3/",
                             "/api/infra/v1/region/digitalocean/nyc1/"]
        nodetype2 = dockercloudcli.commands.dockercloud.NodeType()
        nodetype2.name = '1gb'
        nodetype2.label = '1GB'
        nodetype2.resource_uri = '/api/infra/v1/nodetype/digitalocean/1gb/'
        nodetype2.regions = ["/api/infra/v1/region/digitalocean/ams1/",
                             "/api/infra/v1/region/digitalocean/sfo1/",
                             "/api/infra/v1/region/digitalocean/nyc2/",
                             "/api/infra/v1/region/digitalocean/ams2/",
                             "/api/infra/v1/region/digitalocean/sgp1/",
                             "/api/infra/v1/region/digitalocean/lon1/",
                             "/api/infra/v1/region/digitalocean/nyc3/",
                             "/api/infra/v1/region/digitalocean/nyc1/"]
        nodetype3 = dockercloudcli.commands.dockercloud.NodeType()
        nodetype3.name = '3gb'
        nodetype3.label = '3GB'
        nodetype3.resource_uri = '/api/infra/v1/region/aws/3gb/'
        nodetype3.regions = ["/api/infra/v1/nodetype/aws/tokyo/",
                             "/api/infra/v1/nodetype/aws/kyoto/",
                             "/api/infra/v1/nodetype/aws/shibuya/",
                             "/api/infra/v1/nodetype/aws/ueno/",
                             "/api/infra/v1/nodetype/aws/akiba/"]
        self.nodetypelist = [nodetype1, nodetype2, nodetype3]

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.list')
    def test_nodecluster_show_types(self, mock_list):
        output = '''NAME    LABEL    PROVIDER      REGIONS
512mb   512MB    digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1
1gb     1GB      digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1
3gb     3GB      aws           tokyo, kyoto, shibuya, ueno, akiba'''
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types('', '')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.list')
    def test_nodecluster_show_types_with_provider_filter(self, mock_list):
        output = '''NAME    LABEL    PROVIDER    REGIONS
3gb     3GB      aws         tokyo, kyoto, shibuya, ueno, akiba'''
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types('aws', '')

        self.assertEqual(output, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.list')
    def test_nodecluster_show_types_with_region_filter(self, mock_list):
        output = '''NAME    LABEL    PROVIDER      REGIONS
512mb   512MB    digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1
1gb     1GB      digitalocean  ams1, sfo1, nyc2, ams2, sgp1, lon1, nyc3, nyc1'''
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types(output, 'nyc3')

    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.list')
    def test_nodecluster_show_types_with_filters(self, mock_list):
        mock_list.return_value = self.nodetypelist
        nodecluster_show_types('aws', 'nyc3')

        self.assertEqual('NAME    LABEL    PROVIDER    REGIONS', self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeType.list', side_effect=dockercloud.ApiError)
    def test_nodecluster_show_types_with_exception(self, mock_list, mock_exit):
        nodecluster_show_types('', '')

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)


class NodeClusterCreateTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.deploy')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.save')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.create')
    def test_nodecluster_create(self, mock_create, mock_save, mock_deploy):
        provider_name = 'digitalocean'
        region_name = 'lon1'
        nodetype_name = '1gb'
        region_uri = "/api/infra/v1/region/%s/%s/" % (provider_name, region_name)
        nodetype_uri = "/api/infra/v1/nodetype/%s/%s/" % (provider_name, nodetype_name)
        nodecluster = dockercloudcli.commands.dockercloud.NodeCluster()
        nodecluster.uuid = '7A4CFE51-03BB-42D6-825E-3B533888D8CD'
        mock_create.return_value = nodecluster
        nodecluster_create(3, 'name', provider_name, region_name, nodetype_name, False, None, None, "", [], [], "")

        mock_create.assert_called_with(name='name', target_num_nodes=3, region=region_uri,
                                       node_type=nodetype_uri)
        self.assertEqual(nodecluster.uuid, self.buf.getvalue().strip())
        self.buf.truncate(0)

    @mock.patch('dockercloudcli.commands.sys.exit')
    @mock.patch('dockercloudcli.commands.dockercloud.NodeCluster.create', side_effect=dockercloud.ApiError)
    def test_nodecluster_create_with_exception(self, mock_create, mock_exit):
        nodecluster_create(3, 'name', 'provider', 'region', 'nodetype', False, None, None, "", [], [], "")

        mock_exit.assert_called_with(EXCEPTION_EXIT_CODE)
