import StringIO
import copy
import sys
import unittest

import mock

import dockercloudcli
from dockercloudcli.cli import patch_help_option, dispatch_cmds, initialize_parser
from dockercloudcli.exceptions import InternalError


class PatchHelpOptionTestCase(unittest.TestCase):
    def setUp(self):
        self.add_help_argv_list = [
            ['docker-cloud'],
            ['docker-cloud', 'service'],
            ['docker-cloud', 'service', 'create'],
            ['docker-cloud', 'service', 'inspect'],
            ['docker-cloud', 'service', 'logs'],
            ['docker-cloud', 'service', 'redeploy'],
            ['docker-cloud', 'service', 'run'],
            ['docker-cloud', 'service', 'scale'],
            ['docker-cloud', 'service', 'set'],
            ['docker-cloud', 'service', 'start'],
            ['docker-cloud', 'service', 'stop'],
            ['docker-cloud', 'service', 'terminate'],
            ['docker-cloud', 'container'],
            ['docker-cloud', 'container', 'exec'],
            ['docker-cloud', 'container', 'inspect'],
            ['docker-cloud', 'container', 'logs'],
            ['docker-cloud', 'container', 'start'],
            ['docker-cloud', 'container', 'stop'],
            ['docker-cloud', 'container', 'terminate'],
            ['docker-cloud', 'repository'],
            ['docker-cloud', 'repository', 'register'],
            ['docker-cloud', 'repository', 'rm'],
            ['docker-cloud', 'repository', 'update'],
            ['docker-cloud', 'run'],
            ['docker-cloud', 'exec'],
            ['docker-cloud', 'node'],
            ['docker-cloud', 'node', 'inspect'],
            ['docker-cloud', 'node', 'rm'],
            ['docker-cloud', 'node', 'upgrade'],
            ['docker-cloud', 'nodecluster'],
            ['docker-cloud', 'nodecluster', 'create'],
            ['docker-cloud', 'nodecluster', 'inspect'],
            ['docker-cloud', 'nodecluster', 'rm'],
            ['docker-cloud', 'nodecluster', 'scale'],
            ['docker-cloud', 'tag', 'add'],
            ['docker-cloud', 'tag', 'ls'],
            ['docker-cloud', 'tag', 'rm'],
            ['docker-cloud', 'tag', 'set'],
        ]
        self.not_add_help_argv_list = [
            ["docker-cloud", "service", "ps"],
            ["docker-cloud", "container", "ps"],
            ["docker-cloud", "repository", "ls"],
            ["docker-cloud", "node", "ls"],
            ["docker-cloud", "nodecluster", "ls"],
            ["docker-cloud", "nodecluster", "provider"],
            ["docker-cloud", "nodecluster", "region"],
            ['docker-cloud', 'nodecluster', 'nodetype'],
            ["docker-cloud", "container", "run", "-p", "80:80", "tutum/wordpress"],
        ]

    def test_parser_with_empty_args(self):
        args = []
        self.assertRaises(InternalError, patch_help_option, args)

    def test_help_append(self):
        for argv in self.add_help_argv_list:
            args = patch_help_option(argv)
            target = copy.copy(argv[1:])
            target.append('-h')
            self.assertEqual(target, args, "Help option not patch correctly: %s" % argv)

    def test_help_not_append(self):
        for argv in self.not_add_help_argv_list:
            args = patch_help_option(argv)
            self.assertEqual(argv[1:], args, "Should not patch help option correctly: %s" % argv)

    def test_help_append_with_debug_option(self):
        argvlist = copy.copy(self.add_help_argv_list)
        for argv in argvlist:
            argv.insert(1, "--debug")
            args = patch_help_option(argv)
            target = copy.copy(argv[1:])
            target.append('-h')
            self.assertEqual(target, args, "Help option not patch correctly: %s" % argv)

    def test_help_not_append_with_debug_option(self):
        argvlist = copy.copy(self.not_add_help_argv_list)
        for argv in argvlist:
            argv.insert(1, "--debug")
            args = patch_help_option(argv)
            self.assertEqual(argv[1:], args, "Should not patch help option correctly: %s" % argv)


class CommandsDispatchTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = dockercloudcli.cli.initialize_parser()

    @mock.patch('dockercloudcli.cli.commands')
    def test_run_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['run', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_run.assert_called_with(image=args.image, name=args.name, cpu_shares=args.cpushares,
                                                 memory=args.memory, target_num_containers=args.target_num_containers,
                                                 privileged=args.privileged,
                                                 run_command=args.run_command,
                                                 entrypoint=args.entrypoint, expose=args.expose, publish=args.publish,
                                                 envvars=args.env, envfiles=args.env_file, tag=args.tag,
                                                 linked_to_service=args.link_service,
                                                 autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                 autoredeploy=args.autoredeploy, roles=args.role,
                                                 sequential=args.sequential,
                                                 volume=args.volume, volumes_from=args.volumes_from,
                                                 deployment_strategy=args.deployment_strategy, sync=args.sync,
                                                 net=args.net, pid=args.pid)

    @mock.patch('dockercloudcli.cli.commands')
    def test_exec_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['exec', 'command', 'mysql', '.'])
        dispatch_cmds(args)
        mock_cmds.container_exec.assert_called_with(args.identifier, args.command)

    @mock.patch('dockercloudcli.cli.commands')
    def test_up_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['up'])
        dispatch_cmds(args)
        mock_cmds.stack_up.assert_called_with(args.name, args.file, args.sync)

    @mock.patch('dockercloudcli.cli.commands')
    def test_service_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['service', 'create', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_create.assert_called_with(image=args.image, name=args.name, cpu_shares=args.cpushares,
                                                    memory=args.memory,
                                                    target_num_containers=args.target_num_containers,
                                                    privileged=args.privileged,
                                                    run_command=args.run_command,
                                                    entrypoint=args.entrypoint, expose=args.expose,
                                                    publish=args.publish,
                                                    envvars=args.env, envfiles=args.env_file, tag=args.tag,
                                                    linked_to_service=args.link_service,
                                                    autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                    autoredeploy=args.autoredeploy, roles=args.role,
                                                    sequential=args.sequential,
                                                    volume=args.volume, volumes_from=args.volumes_from,
                                                    deployment_strategy=args.deployment_strategy, sync=args.sync,
                                                    net=args.net, pid=args.pid)

        args = self.parser.parse_args(['service', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'logs', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_logs.assert_called_with(args.identifier, None, False)

        args = self.parser.parse_args(['service', 'ps'])
        dispatch_cmds(args)
        mock_cmds.service_ps.assert_called_with(args.quiet, args.status, args.stack)

        args = self.parser.parse_args(['service', 'redeploy', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_redeploy.assert_called_with(args.identifier, args.not_reuse_volumes, args.sync)

        args = self.parser.parse_args(['service', 'run', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_run.assert_called_with(image=args.image, name=args.name, cpu_shares=args.cpushares,
                                                 memory=args.memory, target_num_containers=args.target_num_containers,
                                                 privileged=args.privileged,
                                                 run_command=args.run_command,
                                                 entrypoint=args.entrypoint, expose=args.expose, publish=args.publish,
                                                 envvars=args.env, envfiles=args.env_file, tag=args.tag,
                                                 linked_to_service=args.link_service,
                                                 autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                 autoredeploy=args.autoredeploy, roles=args.role,
                                                 sequential=args.sequential,
                                                 volume=args.volume, volumes_from=args.volumes_from,
                                                 deployment_strategy=args.deployment_strategy, sync=args.sync,
                                                 net=args.net, pid=args.pid)

        args = self.parser.parse_args(['service', 'scale', 'id', '3'])
        dispatch_cmds(args)
        mock_cmds.service_scale.assert_called_with(args.identifier, args.target_num_containers, args.sync)

        args = self.parser.parse_args(['service', 'set', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_set.assert_called_with(args.identifier, image=args.image, cpu_shares=args.cpushares,
                                                 memory=args.memory, privileged=args.privileged,
                                                 target_num_containers=args.target_num_containers,
                                                 run_command=args.run_command,
                                                 entrypoint=args.entrypoint, expose=args.expose, publish=args.publish,
                                                 envvars=args.env, envfiles=args.env_file,
                                                 tag=args.tag, linked_to_service=args.link_service,
                                                 autorestart=args.autorestart, autodestroy=args.autodestroy,
                                                 autoredeploy=args.autoredeploy, roles=args.role,
                                                 sequential=args.sequential, redeploy=args.redeploy,
                                                 volume=args.volume, volumes_from=args.volumes_from,
                                                 deployment_strategy=args.deployment_strategy, sync=args.sync,
                                                 net=args.net, pid=args.pid)

        args = self.parser.parse_args(['service', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_start.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['service', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_stop.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['service', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_terminate.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['service', 'env', 'add', 'id', '--env', 'abc=abc'])
        dispatch_cmds(args)
        mock_cmds.service_env_add.assert_called_with(args.identifier, envvars=args.env, envfiles=args.env_file,
                                                     redeploy=args.redeploy, sync=args.sync)

        args = self.parser.parse_args(['service', 'env', 'set', 'id', '--env', 'abc=abc'])
        dispatch_cmds(args)
        mock_cmds.service_env_set.assert_called_with(args.identifier, envvars=args.env, envfiles=args.env_file,
                                                     redeploy=args.redeploy, sync=args.sync)

        args = self.parser.parse_args(['service', 'env', 'update', 'id', '--env', 'abc=abc'])
        dispatch_cmds(args)
        mock_cmds.service_env_update.assert_called_with(args.identifier, envvars=args.env, envfiles=args.env_file,
                                                        redeploy=args.redeploy, sync=args.sync)

        args = self.parser.parse_args(['service', 'env', 'rm', 'id', '--name', 'abc'])
        dispatch_cmds(args)
        mock_cmds.service_env_rm.assert_called_with(args.identifier, names=args.name,
                                                    redeploy=args.redeploy, sync=args.sync)

        args = self.parser.parse_args(['service', 'env', 'ls', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_env_ls.assert_called_with(args.identifier, args.quiet, args.user, args.image,
                                                    args.dockercloud)

    @mock.patch('dockercloudcli.cli.commands')
    def test_container_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['container', 'exec', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_exec.assert_called_with(args.identifier, args.command)

        args = self.parser.parse_args(['container', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'logs', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_logs.assert_called_with(args.identifier, None, False)

        args = self.parser.parse_args(['container', 'ps'])
        dispatch_cmds(args)
        mock_cmds.container_ps.assert_called_with(args.quiet, args.status, args.service, args.no_trunc)

        args = self.parser.parse_args(['container', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_start.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['container', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_stop.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['container', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_terminate.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['container', 'redeploy', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_redeploy.assert_called_with(args.identifier, args.not_reuse_volumes, args.sync)

    @mock.patch('dockercloudcli.cli.commands')
    def test_repository_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['repository', 'ls'])
        dispatch_cmds(args)
        mock_cmds.repository_ls.assert_called_with(args.quiet)

        args = self.parser.parse_args(['repository', 'register', 'name'])
        dispatch_cmds(args)
        mock_cmds.repository_register(args.repository_name)

        args = self.parser.parse_args(['repository', 'rm', 'name'])
        dispatch_cmds(args)
        mock_cmds.repository_rm(args.repository_name)

        args = self.parser.parse_args(['repository', 'update', 'name'])
        dispatch_cmds(args)
        mock_cmds.repository_update(args.repository_name, args.username, args.password)

    @mock.patch('dockercloudcli.cli.commands')
    def test_node_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['node', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['node', 'ls'])
        dispatch_cmds(args)
        mock_cmds.node_ls(args.quiet)

        args = self.parser.parse_args(['node', 'rm', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_rm(args.identifier, args.sync)

        args = self.parser.parse_args(['node', 'upgrade', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_rm(args.identifier, args.sync)

    @mock.patch('dockercloudcli.cli.commands')
    def test_nodecluster_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['nodecluster', 'create', 'name', '1', '2', '3'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_create(args.target_num_nodes, args.name,
                                     args.provider, args.region, args.nodetype, args.sync)

        args = self.parser.parse_args(['nodecluster', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_inspect(args.identifier)

        args = self.parser.parse_args(['nodecluster', 'ls'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_ls(args.quiet)

        args = self.parser.parse_args(['nodecluster', 'provider'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_providers(args.quiet)

        args = self.parser.parse_args(['nodecluster', 'region', '-p', 'digitalocean'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_regions(args.provider)

        args = self.parser.parse_args(['nodecluster', 'nodetype', '-r', 'ams1', '-p', 'digitalocean'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_types(args.provider, args.region)

        args = self.parser.parse_args(['nodecluster', 'rm', 'id'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_rm(args.identifier, args.sync)

        args = self.parser.parse_args(['nodecluster', 'scale', 'id', '3'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_scale(args.identifier, args.target_num_nodes, args.sync)

    @mock.patch('dockercloudcli.cli.commands')
    def test_tag_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['tag', 'add', '-t', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_add.assert_called_with(args.identifier, args.tag)

        args = self.parser.parse_args(['tag', 'ls', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_ls.assert_called_with(args.identifier, args.quiet)

        args = self.parser.parse_args(['tag', 'rm', '-t', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_rm.assert_called_with(args.identifier, args.tag)

        args = self.parser.parse_args(['tag', 'set', '-t', 'abc', 'id'])
        dispatch_cmds(args)
        mock_cmds.tag_set.assert_called_with(args.identifier, args.tag)

    @mock.patch('dockercloudcli.cli.commands')
    def test_stack_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['stack', 'create'])
        dispatch_cmds(args)
        mock_cmds.stack_create.assert_called_with(args.name, args.file, args.sync)

        args = self.parser.parse_args(['stack', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['stack', 'ls'])
        dispatch_cmds(args)
        mock_cmds.stack_ls.assert_called_with(args.quiet)

        args = self.parser.parse_args(['stack', 'redeploy', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_redeploy.assert_called_with(args.identifier, args.not_reuse_volumes, args.sync)

        args = self.parser.parse_args(['stack', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_start.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['stack', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_stop.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['stack', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_terminate.assert_called_with(args.identifier, args.sync)

        args = self.parser.parse_args(['stack', 'up'])
        dispatch_cmds(args)
        mock_cmds.stack_up.assert_called_with(args.name, args.file, args.sync)

        args = self.parser.parse_args(['stack', 'update', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_update.assert_called_with(args.identifier, args.file, args.sync)

        args = self.parser.parse_args(['stack', 'export', 'id'])
        dispatch_cmds(args)
        mock_cmds.stack_export.assert_called_with(args.identifier, args.file)


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    def compare_output(self, output, args):
        parser = initialize_parser()
        argv = patch_help_option(args)

        parser.parse_args(argv)

        out = self.buf.getvalue()
        self.buf.truncate(0)

        self.assertEqual(' '.join(output.split()), ' '.join(out.split()))

    @mock.patch('dockercloudcli.cli.argparse.ArgumentParser.add_argument')
    @mock.patch('dockercloudcli.cli.argparse.ArgumentParser.exit')
    def test_dockercloud_version(self, mock_exit, mock_add_arg):
        initialize_parser()
        mock_add_arg.assert_any_call('-v', '--version', action='version',
                                     version='%(prog)s ' + dockercloudcli.__version__)
