# -*- coding: utf-8 -*-
import tempfile
import unittest

import mock

from dockercloudcli.utils import *


class TabulateResultTestCase(unittest.TestCase):
    @mock.patch('dockercloudcli.utils.tabulate')
    def test_tabulate_result(self, mock_tabulate):
        data_list = None
        headers = None
        tabulate_result(data_list, headers)
        mock_tabulate.assert_called_with(data_list, headers, stralign="left", tablefmt="plain")


class DateTimeConversionTestCase(unittest.TestCase):
    def test_from_utc_string_to_utc_datetime(self):
        # test None
        self.assertIsNone(from_utc_string_to_utc_datetime(None))

        # test mal-formatted string
        self.assertRaises(Exception, from_utc_string_to_utc_datetime, 'abc')

        # test normal case
        utc_datetime = from_utc_string_to_utc_datetime('Sun, 6 Apr 2014 18:11:17 +0000')
        self.assertEqual(str(utc_datetime), '2014-04-06 18:11:17')

    def test_get_humanize_local_datetime_from_utc_datetime_string(self):
        # test None
        self.assertEqual(get_humanize_local_datetime_from_utc_datetime_string(None), '')

        # test mal-formatted string
        self.assertRaises(Exception, get_humanize_local_datetime_from_utc_datetime_string, 'abc')

        # test normal case
        utc_datetime = get_humanize_local_datetime_from_utc_datetime_string('Sun, 6 Apr 2014 18:11:17 +0000')
        self.assertRegexpMatches(utc_datetime, r".* ago")

        # test future
        utc_datetime = get_humanize_local_datetime_from_utc_datetime_string('Sun, 6 Apr 3014 18:11:17 +0000')
        self.assertNotRegexpMatches(utc_datetime, r".* ago")


class IsUuidTestCase(unittest.TestCase):
    def test_is_uuid4(self):
        self.assertTrue(is_uuid4('7a4cfe51-038b-42d6-825e-3b533888d8cd'))
        self.assertTrue(is_uuid4('7A4CFE51-03BB-42D6-825E-3B533888D8CD'))

        self.assertFalse(is_uuid4('not_uuid'))
        self.assertFalse(is_uuid4(''))
        self.assertRaises(Exception, is_uuid4, None)
        self.assertRaises(Exception, is_uuid4, 12345)


class AddUnicodeSymbolToStateTestCase(unittest.TestCase):
    def test_add_unicode_symbol_to_state(self):
        for state in ['Running', 'Partly running']:
            self.assertEqual(' '.join([u'▶', state]), add_unicode_symbol_to_state(state))
        for state in ['Init', 'Stopped']:
            self.assertEqual(' '.join([u'◼', state]), add_unicode_symbol_to_state(state))
        for state in ['Starting', 'Stopping', 'Scaling', 'Terminating']:
            self.assertEqual(' '.join([u'⚙', state]), add_unicode_symbol_to_state(state))
        for state in ['Start failed', 'Stopped with errors']:
            self.assertEqual(' '.join([u'!', state]), add_unicode_symbol_to_state(state))
        for state in ['Terminated']:
            self.assertEqual(' '.join([u'✘', state]), add_unicode_symbol_to_state(state))


class ParseLinksTestCase(unittest.TestCase):
    def test_parse_links(self):
        output = [{'to_service': 'mysql', 'name': 'db1'}, {'to_service': 'mariadb', 'name': 'db2'}]
        self.assertEqual(output, parse_links(['mysql:db1', 'mariadb:db2'], 'to_service'))

    def test_parse_links_bad_format(self):
        self.assertRaises(BadParameter, parse_links, ['mysql', 'mariadb'], 'to_service')
        self.assertRaises(BadParameter, parse_links, ['mysql:mysql:mysql', 'mariadb:maria:maria'], 'to_service')
        self.assertRaises(BadParameter, parse_links, [''], 'to_service')


class ParsePublishedPortsTestCase(unittest.TestCase):
    def test_parse_published_ports(self):
        output = [{'protocol': 'tcp', 'inner_port': '80', 'published': True},
                  {'protocol': 'udp', 'inner_port': '53', 'published': True},
                  {'protocol': 'tcp', 'inner_port': '3306', 'outer_port': '3307', 'published': True},
                  {'protocol': 'udp', 'inner_port': '8080', 'outer_port': '8083', 'published': True}]
        self.assertEqual(output, parse_published_ports(['80', '53/udp', '3307:3306', '8083:8080/udp']))

    def test_parse_published_ports_bad_format(self):
        self.assertRaises(BadParameter, parse_published_ports, ['abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['abc:80'])
        self.assertRaises(BadParameter, parse_published_ports, ['80:abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['80:80:abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['80:80/abc'])
        self.assertRaises(BadParameter, parse_published_ports, ['80/80:tcp'])
        self.assertRaises(BadParameter, parse_published_ports, [''])


class ParseExposedPortsTestCase(unittest.TestCase):
    def test_parse_exposed_ports(self):
        output = [{'protocol': 'tcp', 'inner_port': '80', 'published': False},
                  {'protocol': 'tcp', 'inner_port': '8080', 'published': False}]
        self.assertEqual(output, parse_exposed_ports([80, 8080]))

    def test_parse_exposed_ports_bad_format(self):
        self.assertRaises(BadParameter, parse_exposed_ports, ['abc'])
        self.assertRaises(BadParameter, parse_exposed_ports, ['abc'])
        self.assertRaises(BadParameter, parse_exposed_ports, ['-1'])
        self.assertRaises(BadParameter, parse_exposed_ports, ['999999'])


class ParseEnvironmentVariablesTestCase(unittest.TestCase):
    def test_parse_envvars(self):
        output = [{'key': 'MYSQL_PASS', 'value': 'mypass'}, {'key': 'MYSQL_USER', 'value': 'admin'}]
        self.assertEqual(output, parse_envvars(['MYSQL_USER=admin', 'MYSQL_PASS=mypass'], []))


class GetStackNameTestCase(unittest.TestCase):
    def test_update_stack_with_existing_stack(self):
        stack = dockercloud.Stack.create()
        self.assertEqual(stack, update_stack("whatever", stack))

    def test_update_stack_with_empty_stack(self):
        self.assertEqual("name", update_stack("name", None).name)

    @mock.patch('os.path.basename', )
    def test_update_stack_with_empty_stack(self, mock_basename):
        mock_basename.return_value = "basename"
        self.assertEqual("basename", update_stack(None, None).name)


class GetServicesFromStackfilesTestCase(unittest.TestCase):
    def test_get_services_from_stackfiles(self):
        os.environ["DOCKER_HOST"] = "dockerhost"
        os.environ["DOCKER_PATH"] = "dockerpath"
        tempdir = tempfile.mkdtemp("sub")

        self.assertEqual({'name': 'stackname', 'services': []}, get_services_from_stackfiles("stackname", []))

        f1 = open(os.path.join(tempdir, 'docker-cloud.yml'), 'w')
        f1.write('''lb:
  image: dockercloud/haproxy
  environment:
    - DOCKER_HOST
  volumes:
    - $DOCKER_PATH:$DOCKER_PATH
hw1:
  image: dockercloud/hello-world
  ''')
        f1.close()
        data1 = {'services': [{'environment': ['DOCKER_HOST=dockerhost'], 'image': 'dockercloud/haproxy', 'name': 'lb',
                               'volumes': ['dockerpath:dockerpath']},
                              {'image': 'dockercloud/hello-world', 'name': 'hw1'}],
                 'name': 'stackname'}
        self.assertEqual(data1, get_services_from_stackfiles("stackname", [os.path.join(tempdir, 'docker-cloud.yml')]))

        f2 = open(os.path.join(tempdir, 'docker-cloud.override.yml'), 'w')
        f2.write('''hw1:
  image: tutum/hello-world
hw2:
  image: dockercloud/hello-world
''')
        f2.close()
        data2 = {'services': [{'image': 'dockercloud/hello-world', 'name': 'hw2'},
                              {'environment': ['DOCKER_HOST=dockerhost'], 'image': 'dockercloud/haproxy', 'name': 'lb',
                               'volumes': ['dockerpath:dockerpath']},
                              {'image': 'tutum/hello-world', 'name': 'hw1'}],
                 'name': 'stackname'}
        self.assertEqual(data2, get_services_from_stackfiles("stackname", [os.path.join(tempdir, 'docker-cloud.yml'),
                                                                           os.path.join(tempdir,
                                                                                        'docker-cloud.override.yml')]))


class GetStackfilesTestCase(unittest.TestCase):
    def test_get_stackfiles_with_a_list_of_files(self):
        self.assertEqual(["file1", "file2", "file3"], get_stackfiles(["file1", "file2", "file3"]))

    @mock.patch("os.getcwd")
    def test_get_stackfiles_with_not_file_list(self, mock_getcwd):
        tempdir = tempfile.mkdtemp("sub")
        cwd = os.path.join(tempdir, "abc")
        os.mkdir(cwd)
        mock_getcwd.return_value = cwd

        self.assertEqual([], get_stackfiles(None))

        open(os.path.join(tempdir, "docker-compose.yaml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "docker-compose.yaml")], get_stackfiles(None))
        open(os.path.join(tempdir, "docker-compose.override.yaml"), "w").close()
        self.assertEqual(
            [os.path.join(tempdir, "docker-compose.yaml"), os.path.join(tempdir, "docker-compose.override.yaml")],
            get_stackfiles(None))
        open(os.path.join(tempdir, "docker-compose.yml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "docker-compose.yml")], get_stackfiles(None))
        open(os.path.join(tempdir, "docker-compose.override.yml"), "w").close()
        self.assertEqual(
            [os.path.join(tempdir, "docker-compose.yml"), os.path.join(tempdir, "docker-compose.override.yml")],
            get_stackfiles(None))

        open(os.path.join(tempdir, "tutum.yaml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "tutum.yaml")], get_stackfiles(None))
        open(os.path.join(tempdir, "tutum.override.yaml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "tutum.yaml"), os.path.join(tempdir, "tutum.override.yaml")],
                         get_stackfiles(None))
        open(os.path.join(tempdir, "tutum.yml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "tutum.yml")], get_stackfiles(None))
        open(os.path.join(tempdir, "tutum.override.yml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "tutum.yml"), os.path.join(tempdir, "tutum.override.yml")],
                         get_stackfiles(None))

        open(os.path.join(tempdir, "docker-cloud.yaml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "docker-cloud.yaml")], get_stackfiles(None))
        open(os.path.join(tempdir, "docker-cloud.override.yaml"), "w").close()
        self.assertEqual(
            [os.path.join(tempdir, "docker-cloud.yaml"), os.path.join(tempdir, "docker-cloud.override.yaml")],
            get_stackfiles(None))
        open(os.path.join(tempdir, "docker-cloud.yml"), "w").close()
        self.assertEqual([os.path.join(tempdir, "docker-cloud.yml")], get_stackfiles(None))
        open(os.path.join(tempdir, "docker-cloud.override.yml"), "w").close()
        self.assertEqual(
            [os.path.join(tempdir, "docker-cloud.yml"), os.path.join(tempdir, "docker-cloud.override.yml")],
            get_stackfiles(None))

        open(os.path.join(cwd, "docker-compose.yaml"), "w").close()
        self.assertEqual([os.path.join(cwd, "docker-compose.yaml")], get_stackfiles(None))
        open(os.path.join(cwd, "docker-compose.override.yaml"), "w").close()
        self.assertEqual([os.path.join(cwd, "docker-compose.yaml"), os.path.join(cwd, "docker-compose.override.yaml")],
                         get_stackfiles(None))
        open(os.path.join(cwd, "docker-compose.yml"), "w").close()
        self.assertEqual([os.path.join(cwd, "docker-compose.yml")], get_stackfiles(None))
        open(os.path.join(cwd, "docker-compose.override.yml"), "w").close()
        self.assertEqual([os.path.join(cwd, "docker-compose.yml"), os.path.join(cwd, "docker-compose.override.yml")],
                         get_stackfiles(None))
