from __future__ import print_function

import errno
import getpass
import json
import logging
import sys
import urllib

import dockercloud
import websocket
import yaml


from dockercloudcli import utils

AUTH_ERROR_EXIT_CODE = 2
EXCEPTION_EXIT_CODE = 3

cli_log = logging.getLogger("cli")

API_VERSION = "v1"


def login():
    print('''
Please use "docker login" to log into Docker Cloud with you Docker ID"

Alternatively, you can set the following environment variables:

    export DOCKERCLOUD_USER=<docker username>
    export DOCKERCLOUD_PASS=<docker password>
''')


def event():
    def on_error(e):
        print(e, file=sys.stderr)
        if isinstance(e, KeyboardInterrupt):
            exit(0)

    try:
        events = dockercloud.Events()
        events.on_error(on_error)
        events.on_message(lambda m: print(m))
        events.run_forever()
    except KeyboardInterrupt:
        pass
    except dockercloud.AuthError as e:
        print(e, file=sys.stderr)
        sys.exit(AUTH_ERROR_EXIT_CODE)


def service_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            print(json.dumps(service.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_logs(identifiers, tail, follow):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            service.logs(tail, follow, utils.container_service_log_handler)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_ps(quiet, status, stack):
    try:
        headers = ["NAME", "UUID", "STATUS", "#CONTAINERS", "IMAGE", "DEPLOYED", "PUBLIC DNS", "STACK"]

        stack_resource_uri = None
        if stack:
            s = dockercloud.Utils.fetch_remote_stack(stack, raise_exceptions=False)
            if isinstance(s, dockercloud.NonUniqueIdentifier):
                raise dockercloud.NonUniqueIdentifier(
                    "Identifier %s matches more than one stack, please use UUID instead" % stack)
            if isinstance(s, dockercloud.ObjectNotFound):
                raise dockercloud.ObjectNotFound("Identifier '%s' does not match any stack" % stack)
            stack_resource_uri = s.resource_uri
        service_list = dockercloud.Service.list(state=status, stack=stack_resource_uri)

        data_list = []
        long_uuid_list = []
        has_unsynchronized_service = False
        stacks = {}
        for stack in dockercloud.Stack.list():
            stacks[stack.resource_uri] = stack.name
        for service in service_list:
            service_state = utils.add_unicode_symbol_to_state(service.state)
            if not service.synchronized and service.state != "Redeploying":
                service_state += "(*)"
                has_unsynchronized_service = True
            data_list.append([service.name, service.uuid[:8],
                              service_state,
                              service.current_num_containers,
                              service.image_name,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(service.deployed_datetime),
                              service.public_dns,
                              stacks.get(service.stack)])
            long_uuid_list.append(service.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", ""])

        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
            if has_unsynchronized_service:
                print(
                    "\n(*) Please note that this service needs to be redeployed to "
                    "have its configuration changes applied")
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def service_redeploy(identifiers, not_reuse_volume, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            result = service.redeploy(not not_reuse_volume)
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_create(image, name, cpu_shares, memory, privileged, target_num_containers, run_command, entrypoint,
                   expose, publish, envvars, envfiles, tag, linked_to_service, autorestart, autodestroy, autoredeploy,
                   roles, sequential, volume, volumes_from, deployment_strategy, sync, net, pid):
    has_exception = False
    try:
        ports = utils.parse_published_ports(publish)

        # Add exposed_port to ports, excluding whose inner_port that has been defined in published ports
        exposed_ports = utils.parse_exposed_ports(expose)
        for exposed_port in exposed_ports:
            existed = False
            for port in ports:
                if exposed_port.get('inner_port', '') == port.get('inner_port', ''):
                    existed = True
                    break
            if not existed:
                ports.append(exposed_port)

        envvars = utils.parse_envvars(envvars, envfiles)
        links_service = utils.parse_links(linked_to_service, 'to_service')

        tags = []
        if tag:
            if isinstance(tag, list):
                for t in tag:
                    tags.append({"name": t})
            else:
                tags.append({"name": tag})

        bindings = utils.parse_volume(volume)
        bindings.extend(utils.parse_volumes_from(volumes_from))

        service = dockercloud.Service.create(image=image, name=name, cpu_shares=cpu_shares,
                                             memory=memory, privileged=privileged,
                                             target_num_containers=target_num_containers, run_command=run_command,
                                             entrypoint=entrypoint, container_ports=ports, container_envvars=envvars,
                                             linked_to_service=links_service,
                                             autorestart=autorestart, autodestroy=autodestroy,
                                             autoredeploy=autoredeploy,
                                             roles=roles, sequential_deployment=sequential, tags=tags,
                                             bindings=bindings,
                                             deployment_strategy=deployment_strategy, net=net, pid=pid)
        result = service.save()
        if not utils.sync_action(service, sync):
            has_exception = True
        if result:
            print(service.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_run(image, name, cpu_shares, memory, privileged, target_num_containers, run_command, entrypoint,
                expose, publish, envvars, envfiles, tag, linked_to_service, autorestart, autodestroy, autoredeploy,
                roles, sequential, volume, volumes_from, deployment_strategy, sync, net, pid):
    has_exception = False
    try:
        ports = utils.parse_published_ports(publish)

        # Add exposed_port to ports, excluding whose inner_port that has been defined in published ports
        exposed_ports = utils.parse_exposed_ports(expose)
        for exposed_port in exposed_ports:
            existed = False
            for port in ports:
                if exposed_port.get('inner_port', '') == port.get('inner_port', ''):
                    existed = True
                    break
            if not existed:
                ports.append(exposed_port)

        envvars = utils.parse_envvars(envvars, envfiles)
        links_service = utils.parse_links(linked_to_service, 'to_service')

        tags = []
        if tag:
            if isinstance(tag, list):
                for t in tag:
                    tags.append({"name": t})
            else:
                tags.append({"name": tag})

        bindings = utils.parse_volume(volume)
        bindings.extend(utils.parse_volumes_from(volumes_from))

        service = dockercloud.Service.create(image=image, name=name, cpu_shares=cpu_shares,
                                             memory=memory, privileged=privileged,
                                             target_num_containers=target_num_containers, run_command=run_command,
                                             entrypoint=entrypoint, container_ports=ports, container_envvars=envvars,
                                             linked_to_service=links_service,
                                             autorestart=autorestart, autodestroy=autodestroy,
                                             autoredeploy=autoredeploy,
                                             roles=roles, sequential_deployment=sequential, tags=tags,
                                             bindings=bindings,
                                             deployment_strategy=deployment_strategy, net=net, pid=pid)
        service.save()
        result = service.start()
        if not utils.sync_action(service, sync):
            has_exception = True
        if result:
            print(service.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_scale(identifiers, target_num_containers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            service.target_num_containers = target_num_containers
            service.save()
            result = service.scale()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_set(identifiers, image, cpu_shares, memory, privileged, target_num_containers, run_command, entrypoint,
                expose, publish, envvars, envfiles, tag, linked_to_service, autorestart, autodestroy, autoredeploy,
                roles, sequential, redeploy, volume, volumes_from, deployment_strategy, sync, net, pid):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier, raise_exceptions=True)
            if service is not None:
                if image:
                    service.image = image
                if cpu_shares:
                    service.cpu_shares = cpu_shares
                if memory:
                    service.memory = memory
                if privileged is not None:
                    service.privileged = privileged
                if target_num_containers:
                    service.target_num_containers = target_num_containers
                if run_command:
                    service.run_command = run_command
                if entrypoint:
                    service.entrypoint = entrypoint

                ports = utils.parse_published_ports(publish)
                # Add exposed_port to ports, excluding whose inner_port that has been defined in published ports
                exposed_ports = utils.parse_exposed_ports(expose)
                for exposed_port in exposed_ports:
                    existed = False
                    for port in ports:
                        if exposed_port.get('inner_port', '') == port.get('inner_port', ''):
                            existed = True
                            break
                    if not existed:
                        ports.append(exposed_port)
                if ports:
                    service.container_ports = ports

                envvars = utils.parse_envvars(envvars, envfiles)
                if envvars:
                    service.container_envvars = envvars

                if tag:
                    service.tags = []
                    for t in tag:
                        new_tag = {"name": t}
                        if new_tag not in service.tags:
                            service.tags.append(new_tag)
                    service.__addchanges__("tags")

                links_service = utils.parse_links(linked_to_service, 'to_service')
                if linked_to_service:
                    service.linked_to_service = links_service

                if autorestart:
                    service.autorestart = autorestart

                if autodestroy:
                    service.autodestroy = autodestroy

                if autoredeploy is not None:
                    service.autoredeploy = autoredeploy

                if roles:
                    service.roles = roles

                if sequential is not None:
                    service.sequential_deployment = sequential

                bindings = utils.parse_volume(volume)
                bindings.extend(utils.parse_volumes_from(volumes_from))
                if bindings:
                    service.bindings = bindings

                if deployment_strategy:
                    service.deployment_strategy = deployment_strategy

                if net:
                    service.net = net

                if pid:
                    service.pid = pid

                result = service.save()
                if not utils.sync_action(service, sync):
                    has_exception = True
                if result:
                    if redeploy:
                        print("Redeploying Service ...")
                        result2 = service.redeploy()
                        if not utils.sync_action(service, sync):
                            has_exception = True
                        if result2:
                            print(service.uuid)
                    else:
                        print(service.uuid)
                        print("Service must be redeployed to have its configuration changes applied.")
                        print("To redeploy execute: $ docker-cloud service redeploy", identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_start(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            result = service.start()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_stop(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            result = service.stop()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_terminate(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            result = service.delete()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                print(service.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_exec(identifier, command):
    try:
        import termios
        import tty
        import select
        import signal
    except ImportError:
        print("docker-cloud exec is not supported on this operating system", file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)

    def invoke_shell(url):
        header = {'User-Agent': dockercloud.user_agent}
        header.update(dockercloud.auth.get_auth_header())

        h = [": ".join([key, value]) for key, value in header.items()]
        cli_log.info("websocket: %s %s" % (url, h))
        shell = websocket.create_connection(url, timeout=10, header=h)

        oldtty = None
        try:
            oldtty = termios.tcgetattr(sys.stdin)
        except:
            pass

        old_handler = signal.getsignal(signal.SIGWINCH)
        errorcode = 0

        try:
            if oldtty:
                tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())

            while True:
                try:
                    if oldtty:
                        r, w, e = select.select([shell.sock, sys.stdin], [], [shell.sock], 5)
                        if sys.stdin in r:
                            x = sys.stdin.read(1)
                            # read arrows
                            if x == '\x1b':
                                x += sys.stdin.read(1)
                                if x[1] == '[':
                                    x += sys.stdin.read(1)
                            if len(x) == 0:
                                shell.send('\n')
                            shell.send(x)
                    else:
                        x = str(sys.stdin.read())
                        r, w, e = select.select([shell.sock], [], [shell.sock], 1)
                        shell.send(x)
                        shell.send(u"\u0004")

                    if shell.sock in r:
                        data = shell.recv()
                        if not data:
                            continue
                        try:
                            message = json.loads(data)
                            if message.get("type") == "error":
                                if message.get("data", {}).get("errorMessage") == "UNAUTHORIZED":
                                    raise dockercloud.AuthError
                                else:
                                    raise dockercloud.ApiError(message)
                            streamType = message.get("streamType")
                            if streamType == "stdout":
                                sys.stdout.write(message.get("output"))
                                sys.stdout.flush()
                            elif streamType == "stderr":
                                sys.stderr.write(message.get("output"))
                                sys.stderr.flush()
                        except dockercloud.AuthError:
                            raise
                        except:
                            sys.stdout.write(data)
                            sys.stdout.flush()
                except (select.error, IOError) as e:
                    if e.args and e.args[0] == errno.EINTR:
                        pass
                    else:
                        raise
        except dockercloud.AuthError:
            sys.stderr.write("Not Authorized\r\n")
            sys.stderr.flush()
            errorcode = AUTH_ERROR_EXIT_CODE
        except websocket.WebSocketConnectionClosedException:
            pass
        except websocket.WebSocketException:
            sys.stderr.write("Connection is already closed.\r\n")
            sys.stderr.flush()
            errorcode = EXCEPTION_EXIT_CODE
        except Exception as e:
            sys.stderr.write("%s\r\n" % e)
            sys.stderr.flush()
            errorcode = EXCEPTION_EXIT_CODE
        finally:
            if oldtty:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
            signal.signal(signal.SIGWINCH, old_handler)
            exit(errorcode)

    try:
        container = dockercloud.Utils.fetch_remote_container(identifier)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)

    endpoint = "api/app/%s/container/%s/exec/?" % (API_VERSION, container.uuid)

    if command:
        escaped_cmd = []
        for c in command:
            if r'"' in c:
                c = c.replace(r'"', r'\"')
            if " " in c:
                c = '"%s"' % c
            escaped_cmd.append(c)

        escaped_cmd = " ".join(escaped_cmd)
        cli_log.debug("escaped command: %s" % escaped_cmd)
        endpoint = "%s&command=%s" % (endpoint, urllib.quote_plus(escaped_cmd))

    url = "/".join([dockercloud.stream_host.rstrip("/"), endpoint.lstrip('/')])
    invoke_shell(url)


def container_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            container = dockercloud.Utils.fetch_remote_container(identifier)
            print(json.dumps(container.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_logs(identifiers, tail, follow):
    has_exception = False
    for identifier in identifiers:
        try:
            container = dockercloud.Utils.fetch_remote_container(identifier)
            container.logs(tail, follow, utils.container_service_log_handler)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_redeploy(identifiers, not_reuse_volume, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            container = dockercloud.Utils.fetch_remote_container(identifier)
            result = container.redeploy(not not_reuse_volume)
            if not utils.sync_action(container, sync):
                has_exception = True
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_ps(quiet, status, service, no_trunc):
    try:
        headers = ["NAME", "UUID", "STATUS", "IMAGE", "RUN COMMAND", "EXIT CODE", "DEPLOYED", "PORTS", "NODE", "STACK"]

        service_resource_uri = None
        if service:
            s = dockercloud.Utils.fetch_remote_service(service, raise_exceptions=False)
            if isinstance(s, dockercloud.NonUniqueIdentifier):
                raise dockercloud.NonUniqueIdentifier(
                    "Identifier %s matches more than one service, please use UUID instead" % service)
            if isinstance(s, dockercloud.ObjectNotFound):
                raise dockercloud.ObjectNotFound("Identifier '%s' does not match any service" % service)
            service_resource_uri = s.resource_uri

        containers = dockercloud.Container.list(state=status, service=service_resource_uri)

        data_list = []
        long_uuid_list = []
        stacks = {}
        for stack in dockercloud.Stack.list():
            stacks[stack.resource_uri] = stack.name
        services = {}
        for s in dockercloud.Service.list():
            services[s.resource_uri] = s.stack
        nodes = {}
        for n in dockercloud.Node.list():
            nodes[n.resource_uri] = n.uuid

        for container in containers:
            ports = []
            for index, port in enumerate(container.container_ports):
                ports_string = ""
                if port['outer_port'] is not None:
                    ports_string += "%s:%d->" % (container.public_dns, port['outer_port'])
                ports_string += "%d/%s" % (port['inner_port'], port['protocol'])
                ports.append(ports_string)

            container_uuid = container.uuid
            run_command = container.run_command
            ports_string = ", ".join(ports)
            node = nodes.get(container.node)
            if not no_trunc:
                container_uuid = container_uuid[:8]

                if run_command and len(run_command) > 20:
                    run_command = run_command[:17] + '...'
                if ports_string and len(ports_string) > 20:
                    ports_string = ports_string[:17] + '...'
                node = node[:8]

            data_list.append([container.name,
                              container_uuid,
                              utils.add_unicode_symbol_to_state(container.state),
                              container.image_name,
                              run_command,
                              container.exit_code,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(container.deployed_datetime),
                              ports_string,
                              node,
                              stacks.get(services.get(container.service))])
            long_uuid_list.append(container.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def container_start(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            container = dockercloud.Utils.fetch_remote_container(identifier)
            result = container.start()
            if not utils.sync_action(container, sync):
                has_exception = True
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_stop(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            container = dockercloud.Utils.fetch_remote_container(identifier)
            result = container.stop()
            if not utils.sync_action(container, sync):
                has_exception = True
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def container_terminate(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            container = dockercloud.Utils.fetch_remote_container(identifier)
            result = container.delete()
            if not utils.sync_action(container, sync):
                has_exception = True
            if result:
                print(container.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def repository_ls(quiet):
    try:
        headers = ["NAME", "IN_USE"]
        data_list = []
        name_list = []

        repositories = dockercloud.Repository.list()
        if len(repositories) != 0:
            for repository in repositories:
                data = [repository.name]

                if repository.in_use:
                    data.append("yes")
                else:
                    data.append("no")

                data_list.append(data)
                name_list.append(repository.name)
        else:
            data_list.append(["", ""])

        if quiet:
            for name in name_list:
                print(name)
        else:
            utils.tabulate_result(data_list, headers)

    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def repository_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                repository = dockercloud.Repository.fetch(identifier)
            except Exception:
                raise dockercloud.ObjectNotFound("Cannot find a repository with the identifier '%s'" % identifier)
            print(json.dumps(repository.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def repository_register(identifier, username, password):
    if not username and not password:
        print('Please input username and password of the registry:')
        username = raw_input('Username: ')
        password = getpass.getpass()
    elif not username:
        print('Please input username of the registry:')
        username = raw_input('Username: ')
    elif not password:
        print('Please input password of the registry:')
        password = getpass.getpass()
    try:
        repository = dockercloud.Repository.create(name=identifier, username=username, password=password)
        result = repository.save()
        if result:
            print(repository.name)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def repository_rm(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            repository = dockercloud.Repository.fetch(identifier)
            result = repository.delete()
            if result:
                print(identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def repository_update(identifiers, username, password):
    has_exception = False
    for identifier in identifiers:
        try:
            repository = dockercloud.Repository.fetch(identifier)
            if username is not None:
                repository.username = username
            if password is not None:
                repository.password = password
            result = repository.save()
            if result:
                print(repository.name)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_ls(quiet):
    try:
        headers = ["UUID", "FQDN", "LASTSEEN", "STATUS", "CLUSTER", "DOCKER_VER"]
        node_list = dockercloud.Node.list()
        data_list = []
        long_uuid_list = []
        for node in node_list:
            cluster_name = node.node_cluster
            try:
                cluster_name = dockercloud.NodeCluster.fetch(node.node_cluster.strip("/").split("/")[-1]).name
            except:
                pass

            data_list.append([node.uuid[:8],
                              node.external_fqdn,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(node.last_seen),
                              utils.add_unicode_symbol_to_state(node.state),
                              cluster_name, node.docker_version])
            long_uuid_list.append(node.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def node_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            node = dockercloud.Utils.fetch_remote_node(identifier)
            print(json.dumps(dockercloud.Node.fetch(node.uuid).get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_rm(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            node = dockercloud.Utils.fetch_remote_node(identifier)
            result = node.delete()
            if not utils.sync_action(node, sync):
                has_exception = True
            if result:
                print(node.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_upgrade(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            node = dockercloud.Utils.fetch_remote_node(identifier)
            result = node.upgrade_docker()
            if not utils.sync_action(node, sync):
                has_exception = True
            if result:
                print(node.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def node_byo():
    token = ""
    try:
        json = dockercloud.api.http.send_request("POST", "api/infra/%s/token" % API_VERSION)
        if json:
            token = json.get("token", "")
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)

    print("Docker Cloud lets you use your own servers as nodes to run containers. "
          "For this you have to install our agent.")
    print("Run the following command on your server:")
    print()
    print("\tcurl -Ls https://get.cloud.docker.com/ | sudo -H sh -s", token)
    print()


def nodecluster_ls(quiet):
    try:
        headers = ["NAME", "UUID", "REGION", "TYPE", "DEPLOYED", "STATUS", "CURRENT#NODES", "TARGET#NODES"]
        nodecluster_list = dockercloud.NodeCluster.list()
        data_list = []
        long_uuid_list = []
        for nodecluster in nodecluster_list:
            if quiet:
                long_uuid_list.append(nodecluster.uuid)
                continue

            node_type = nodecluster.node_type
            region = nodecluster.region
            try:
                node_type = dockercloud.NodeType.fetch(
                    nodecluster.node_type.strip("/").split("api/infra/%s/nodetype/" % API_VERSION)[-1]).label
                region = dockercloud.Region.fetch(
                    nodecluster.region.strip("/").split("api/infra/%s/region/" % API_VERSION)[-1]).label
            except Exception:
                pass

            data_list.append([nodecluster.name,
                              nodecluster.uuid[:8],
                              region,
                              node_type,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(nodecluster.deployed_datetime),
                              nodecluster.state,
                              nodecluster.current_num_nodes,
                              nodecluster.target_num_nodes])
            long_uuid_list.append(nodecluster.uuid)
        if len(data_list) == 0:
            data_list.append(["", "", "", "", "", "", "", ""])
        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            nodecluster = dockercloud.Utils.fetch_remote_nodecluster(identifier)
            print(json.dumps(dockercloud.NodeCluster.fetch(nodecluster.uuid).get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_show_providers(quiet):
    try:
        headers = ["NAME", "LABEL"]
        data_list = []
        name_list = []
        provider_list = dockercloud.Provider.list()
        for provider in provider_list:
            if quiet:
                name_list.append(provider.name)
                continue

            data_list.append([provider.name, provider.label])

        if len(data_list) == 0:
            data_list.append(["", ""])
        if quiet:
            for name in name_list:
                print(name)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_show_regions(provider):
    try:
        headers = ["NAME", "LABEL", "PROVIDER"]
        data_list = []
        region_list = dockercloud.Region.list()
        for region in region_list:
            provider_name = region.resource_uri.strip("/").split("/")[-2]
            if provider and provider != provider_name:
                continue
            data_list.append([region.name, region.label, provider_name])

        if len(data_list) == 0:
            data_list.append(["", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_show_types(provider, region):
    try:
        headers = ["NAME", "LABEL", "PROVIDER", "REGIONS"]
        data_list = []
        nodetype_list = dockercloud.NodeType.list()
        for nodetype in nodetype_list:
            provider_name = nodetype.resource_uri.strip("/").split("/")[-2]
            regions = [region_uri.strip("/").split("/")[-1] for region_uri in nodetype.regions]
            if provider and provider != provider_name:
                continue

            if region and region not in regions:
                continue
            data_list.append([nodetype.name, nodetype.label, provider_name,
                              ", ".join(regions)])

        if len(data_list) == 0:
            data_list.append(["", "", "", ""])
        utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_create(target_num_nodes, name, provider, region, nodetype, sync, disk, tags, aws_vpc_id,
                       aws_vpc_subnets, aws_vpc_security_groups, aws_iam_instance_profile_name):
    has_exception = False

    region_uri = "/api/infra/%s/region/%s/%s/" % (API_VERSION, provider, region)
    nodetype_uri = "/api/infra/%s/nodetype/%s/%s/" % (API_VERSION, provider, nodetype)

    provider_options = {}
    aws_vpc = {}
    aws_iam = {}

    if aws_iam_instance_profile_name:
        aws_iam["instance_profile_name"] = aws_iam_instance_profile_name
    if aws_vpc_id:
        aws_vpc["id"] = aws_vpc_id
    if aws_vpc_subnets:
        aws_vpc["subnets"] = aws_vpc_subnets
    if aws_vpc_security_groups:
        aws_vpc["security_groups"] = aws_vpc_security_groups
    if aws_vpc:
        provider_options["vpc"] = aws_vpc
    if aws_iam:
        provider_options["iam"] = aws_iam

    args = {'name': name, 'target_num_nodes': target_num_nodes, 'region': region_uri, 'node_type': nodetype_uri}
    if disk:
        args["disk"] = disk
    if provider_options:
        args["provider_options"] = provider_options
    if tags:
        args["tags"] = [{'name': tag} for tag in tags]
    try:
        nodecluster = dockercloud.NodeCluster.create(**args)
        nodecluster.save()
        result = nodecluster.deploy()
        if not utils.sync_action(nodecluster, sync):
            has_exception = True
        if result:
            print(nodecluster.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_rm(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            nodecluster = dockercloud.Utils.fetch_remote_nodecluster(identifier)
            result = nodecluster.delete()
            if not utils.sync_action(nodecluster, sync):
                has_exception = True
            if result:
                print(nodecluster.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_scale(identifiers, target_num_nodes, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            nodecluster = dockercloud.Utils.fetch_remote_nodecluster(identifier)
            nodecluster.target_num_nodes = target_num_nodes
            result = nodecluster.save()
            if not utils.sync_action(nodecluster, sync):
                has_exception = True
            if result:
                print(nodecluster.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def nodecluster_az(quiet):
    try:
        headers = ["NAME", "AVAILABLE", "RESOURCE URI"]
        az_list = dockercloud.AZ.list()
        data_list = []
        long_uuid_list = []
        for az in az_list:
            data_list.append([az.name, "Yes" if az.available else "No", az.resource_uri])
            long_uuid_list.append(az.name)

        if len(data_list) == 0:
            data_list.append(["", "", "", "", ""])

        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_add(identifiers, tags):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                obj = dockercloud.Utils.fetch_remote_service(identifier)
            except dockercloud.ObjectNotFound:
                try:
                    obj = dockercloud.Utils.fetch_remote_nodecluster(identifier)
                except dockercloud.ObjectNotFound:
                    try:
                        obj = dockercloud.Utils.fetch_remote_node(identifier)
                    except dockercloud.ObjectNotFound:
                        raise dockercloud.ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)

            tag = dockercloud.Tag.fetch(obj)
            tag.add(tags)
            tag.save()
            print(obj.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_ls(identifiers, quiet):
    has_exception = False

    headers = ["IDENTIFIER", "TYPE", "TAGS"]
    data_list = []
    tags_list = []
    for identifier in identifiers:
        try:
            obj = dockercloud.Utils.fetch_remote_service(identifier, raise_exceptions=False)
            if isinstance(obj, dockercloud.ObjectNotFound):
                obj = dockercloud.Utils.fetch_remote_nodecluster(identifier, raise_exceptions=False)
                if isinstance(obj, dockercloud.ObjectNotFound):
                    obj = dockercloud.Utils.fetch_remote_node(identifier, raise_exceptions=False)
                    if isinstance(obj, dockercloud.ObjectNotFound):
                        raise dockercloud.ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)
                    else:
                        obj_type = 'Node'
                else:
                    obj_type = 'NodeCluster'
            else:
                obj_type = 'Service'

            tagnames = []
            for tags in dockercloud.Tag.fetch(obj).list():
                tagname = tags.get('name', '')
                if tagname:
                    tagnames.append(tagname)

            data_list.append([identifier, obj_type, ' '.join(tagnames)])
            tags_list.append(' '.join(tagnames))
        except Exception as e:
            if isinstance(e, dockercloud.ObjectNotFound):
                data_list.append([identifier, 'None', ''])
            else:
                data_list.append([identifier, '', ''])
            tags_list.append('')
            print(e, file=sys.stderr)
            has_exception = True
    if quiet:
        for tags in tags_list:
            print(tags)
    else:
        utils.tabulate_result(data_list, headers)
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_rm(identifiers, tags):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                obj = dockercloud.Utils.fetch_remote_service(identifier)
            except dockercloud.ObjectNotFound:
                try:
                    obj = dockercloud.Utils.fetch_remote_nodecluster(identifier)
                except dockercloud.ObjectNotFound:
                    try:
                        obj = dockercloud.Utils.fetch_remote_node(identifier)
                    except dockercloud.ObjectNotFound:
                        raise dockercloud.ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)

            tag = dockercloud.Tag.fetch(obj)
            for t in tags:
                try:
                    tag.delete(t)
                except Exception as e:
                    print(e, file=sys.stderr)
                    has_exception = True
            print(obj.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def tag_set(identifiers, tags):
    has_exception = False
    for identifier in identifiers:
        try:
            try:
                obj = dockercloud.Utils.fetch_remote_service(identifier)
            except dockercloud.ObjectNotFound:
                try:
                    obj = dockercloud.Utils.fetch_remote_nodecluster(identifier)
                except dockercloud.ObjectNotFound:
                    try:
                        obj = dockercloud.Utils.fetch_remote_node(identifier)
                    except dockercloud.ObjectNotFound:
                        raise dockercloud.ObjectNotFound(
                            "Identifier '%s' does not match any service, node or nodecluster" % identifier)

            obj.tags = []
            for t in tags:
                new_tag = {"name": t}
                if new_tag not in obj.tags:
                    obj.tags.append(new_tag)
            obj.__addchanges__("tags")
            obj.save()

            print(obj.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def trigger_create(identifier, name, operation):
    has_exception = False
    try:
        service = dockercloud.Utils.fetch_remote_service(identifier)
        trigger = dockercloud.Trigger.fetch(service)
        trigger.add(name, operation)
        trigger.save()
        print(service.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def trigger_ls(identifier, quiet):
    headers = ["UUID", "NAME", "OPERATION", "URL"]
    data_list = []
    uuid_list = []
    try:
        service = dockercloud.Utils.fetch_remote_service(identifier)
        trigger = dockercloud.Trigger.fetch(service)
        triggers = trigger.list()
        for t in triggers:
            url = dockercloud.rest_host + t.get('url', '/')[1:]
            data_list.append([t.get('uuid', '')[:8], t.get('name', ''), t.get('operation', ''), url])
            uuid_list.append(t.get('uuid', ''))
        if quiet:
            for uuid in uuid_list:
                print(uuid)
        else:
            if len(data_list) == 0:
                data_list.append(['', '', '', ''])
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)


def trigger_rm(identifier, trigger_identifiers):
    has_exception = False
    try:
        service = dockercloud.Utils.fetch_remote_service(identifier)
        trigger = dockercloud.Trigger.fetch(service)
        uuid_list = utils.get_uuids_of_trigger(trigger, trigger_identifiers)
        try:
            for uuid in uuid_list:
                trigger.delete(uuid)
                print(uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_up(name, files, sync):
    has_exception = False
    try:
        stack = utils.load_stackfiles(name=name, files=files)
        stack.save()
        result = stack.start()
        if not utils.sync_action(stack, sync):
            has_exception = True
        if result:
            print(stack.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_create(name, files, sync):
    has_exception = False
    try:
        stack = utils.load_stackfiles(name=name, files=files)
        result = stack.save()
        if not utils.sync_action(stack, sync):
            has_exception = True
        if result:
            print(stack.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = dockercloud.Utils.fetch_remote_stack(identifier)
            print(json.dumps(stack.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_ls(quiet):
    try:
        headers = ["NAME", "UUID", "STATUS", "DEPLOYED", "DESTROYED"]
        stack_list = dockercloud.Stack.list()
        data_list = []
        long_uuid_list = []
        for stack in stack_list:
            data_list.append([stack.name,
                              stack.uuid[:8],
                              utils.add_unicode_symbol_to_state(stack.state),
                              utils.get_humanize_local_datetime_from_utc_datetime_string(stack.deployed_datetime),
                              utils.get_humanize_local_datetime_from_utc_datetime_string(stack.destroyed_datetime)])
            long_uuid_list.append(stack.uuid)

        if len(data_list) == 0:
            data_list.append(["", "", "", "", ""])

        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_redeploy(identifiers, not_reuse_volume, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = dockercloud.Utils.fetch_remote_stack(identifier)
            result = stack.redeploy(not not_reuse_volume)
            if not utils.sync_action(stack, sync):
                has_exception = True
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_start(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = dockercloud.Utils.fetch_remote_stack(identifier)
            result = stack.start()
            if not utils.sync_action(stack, sync):
                has_exception = True
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_stop(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = dockercloud.Utils.fetch_remote_stack(identifier)
            result = stack.stop()
            if not utils.sync_action(stack, sync):
                has_exception = True
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_terminate(identifiers, sync):
    has_exception = False
    for identifier in identifiers:
        try:
            stack = dockercloud.Utils.fetch_remote_stack(identifier)
            result = stack.delete()
            if not utils.sync_action(stack, sync):
                has_exception = True
            if result:
                print(stack.uuid)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_update(identifier, files, sync):
    has_exception = False
    try:
        stack = utils.load_stackfiles(name=None, files=files,
                                      stack=dockercloud.Utils.fetch_remote_stack(identifier))
        result = stack.save()
        if not utils.sync_action(stack, sync):
            has_exception = True
        if result:
            print(stack.uuid)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def stack_export(identifier, stackfile):
    try:
        stack = dockercloud.Utils.fetch_remote_stack(identifier)
        content = stack.export()
        if content:
            if stackfile:
                with open(stackfile, 'w') as outfile:
                    outfile.write(yaml.safe_dump(content, default_flow_style=False, allow_unicode=True))
            else:
                print(yaml.safe_dump(content, default_flow_style=False, allow_unicode=True))

    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def action_inspect(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            action = dockercloud.Utils.fetch_remote_action(identifier)
            print(json.dumps(action.get_all_attributes(), indent=2))
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def action_cancel(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            action = dockercloud.Utils.fetch_remote_action(identifier)
            action.cancel()
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def action_retry(identifiers):
    has_exception = False
    for identifier in identifiers:
        try:
            action = dockercloud.Utils.fetch_remote_action(identifier)
            action.retry()
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def action_ls(quiet, last):
    try:
        headers = ["UUID", "ACTION", "START", "END", "TARGET", "IP", "LOCATION"]
        action_list = dockercloud.Action.list(25 if not last else last)
        data_list = []
        long_uuid_list = []
        for action in action_list:
            terms = action.object.strip("/").split("/", 3)
            target = terms[3] if len(terms) == 4 else ""
            data_list.append([action.uuid[:8],
                              action.action,
                              utils.get_humanize_local_datetime_from_utc_datetime_string(action.start_date),
                              utils.get_humanize_local_datetime_from_utc_datetime_string(action.end_date),
                              target, action.ip, action.location])
            long_uuid_list.append(action.uuid)

        if len(data_list) == 0:
            data_list.append(["", "", "", "", ""])

        if quiet:
            for uuid in long_uuid_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)


def action_logs(identifiers, tail, follow):
    has_exception = False
    for identifier in identifiers:
        try:
            action = dockercloud.Utils.fetch_remote_action(identifier)
            action.logs(tail, follow, utils.action_log_handler)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_env_add(identifiers, envvars, envfiles, redeploy, sync):
    has_exception = False
    input_envvars = utils.parse_envvars(envvars, envfiles)
    if not input_envvars:
        print("Environment variables cannot be empty.", file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            existing_envvar_keys = [env["key"] for env in service.calculated_envvars]
            new_envvars = []
            for envvar in input_envvars:
                if envvar["key"] not in existing_envvar_keys:
                    new_envvars.append(envvar)
                else:
                    print("Failed to add environment variable: \"%s\" already exist in service %s" %
                          (envvar["key"], identifier), file=sys.stderr)
                    has_exception = True

            if not new_envvars:
                print("No environment variables need to be added to service %s" % identifier, file=sys.stderr)
                sys.exit(EXCEPTION_EXIT_CODE)

            existing_envvars = [{"key": env["key"], "value": env["value"]} for env in service.calculated_envvars
                                if env["origin"] == "user"]
            new_envvars.extend(existing_envvars)
            service.container_envvars = new_envvars
            result = service.save()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                if redeploy:
                    print("Redeploying Service ...")
                    result2 = service.redeploy()
                    if not utils.sync_action(service, sync):
                        has_exception = True
                    if result2:
                        print(service.uuid)
                else:
                    print(service.uuid)
                    print("Service must be redeployed to have its configuration changes applied.")
                    print("To redeploy execute: $ docker-cloud service redeploy", identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_env_ls(identifier, quiet, origin_user, origin_image, origin_dockercloud):
    has_exception = False
    try:
        service = dockercloud.Utils.fetch_remote_service(identifier)
        headers = ["ORIGIN", "KEY", "VALUE"]
        data_list = []
        key_value_list = []
        origin_all = not origin_user and not origin_image and not origin_dockercloud
        for envvars in service.calculated_envvars:
            if origin_all or \
                    (origin_user and envvars["origin"] == "user") or \
                    (origin_image and envvars["origin"] == "image") or \
                    (origin_dockercloud and envvars["origin"] == "tutum"):
                data_list.append([envvars["origin"], envvars["key"], envvars["value"]])
                key_value_list.append("%s=%s" % (envvars["key"], envvars["value"]))

        if len(data_list) == 0:
            data_list.append(["", "", ""])

        if quiet:
            for uuid in key_value_list:
                print(uuid)
        else:
            utils.tabulate_result(data_list, headers)
    except Exception as e:
        print(e, file=sys.stderr)
        has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_env_rm(identifiers, names, redeploy, sync):
    has_exception = False
    if not names:
        print("Names of the environment variables cannot be empty.", file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            existing_envvar_keys = [env["key"] for env in service.calculated_envvars if env["origin"] == "user"]

            names_to_be_removed = []

            for name in names:
                if name not in existing_envvar_keys:
                    print("Failed to remove environment variable: \"%s\" is not a user defined environment "
                          "in service %s" % (name, identifier), file=sys.stderr)
                else:
                    names_to_be_removed.append(name)

            new_envvars = [{"key": env["key"], "value": env["value"]} for env in service.calculated_envvars
                           if env["origin"] == "user" and env["key"] not in names_to_be_removed]

            if not names_to_be_removed:
                print("No environment variables need to be removed from service %s" % identifier, file=sys.stderr)
                sys.exit(EXCEPTION_EXIT_CODE)

            service.container_envvars = new_envvars
            result = service.save()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                if redeploy:
                    print("Redeploying Service ...")
                    result2 = service.redeploy()
                    if not utils.sync_action(service, sync):
                        has_exception = True
                    if result2:
                        print(service.uuid)
                else:
                    print(service.uuid)
                    print("Service must be redeployed to have its configuration changes applied.")
                    print("To redeploy execute: $ docker-cloud service redeploy", identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_env_set(identifiers, envvars, envfiles, redeploy, sync):
    has_exception = False
    input_envvars = utils.parse_envvars(envvars, envfiles)
    if not input_envvars:
        print("Environment variables cannot be empty.", file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            service.container_envvars = input_envvars
            result = service.save()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                if redeploy:
                    print("Redeploying Service ...")
                    result2 = service.redeploy()
                    if not utils.sync_action(service, sync):
                        has_exception = True
                    if result2:
                        print(service.uuid)
                else:
                    print(service.uuid)
                    print("Service must be redeployed to have its configuration changes applied.")
                    print("To redeploy execute: $ docker-cloud service redeploy", identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)


def service_env_update(identifiers, envvars, envfiles, redeploy, sync):
    has_exception = False
    input_envvars = utils.parse_envvars(envvars, envfiles)
    if not input_envvars:
        print("Environment variables cannot be empty.", file=sys.stderr)
        sys.exit(EXCEPTION_EXIT_CODE)
    for identifier in identifiers:
        try:
            service = dockercloud.Utils.fetch_remote_service(identifier)
            existing_envvar_keys = [env["key"] for env in service.calculated_envvars]
            new_envvars = []
            for envvar in input_envvars:
                if envvar["key"] in existing_envvar_keys:
                    new_envvars.append(envvar)
                else:
                    print("Failed to update environment variable: \"%s\" does not exist in service %s" %
                          (envvar["key"], identifier), file=sys.stderr)
                    has_exception = True

            if not new_envvars:
                print("No environment variables need to be updated in service %s" % identifier, file=sys.stderr)
                sys.exit(EXCEPTION_EXIT_CODE)

            new_envvar_keys = [env["key"] for env in new_envvars]
            existing_envvars = [{"key": env["key"], "value": env["value"]} for env in service.calculated_envvars
                                if env["origin"] == "user" and env["key"] not in new_envvar_keys]

            new_envvars.extend(existing_envvars)
            service.container_envvars = new_envvars
            result = service.save()
            if not utils.sync_action(service, sync):
                has_exception = True
            if result:
                if redeploy:
                    print("Redeploying Service ...")
                    result2 = service.redeploy()
                    if not utils.sync_action(service, sync):
                        has_exception = True
                    if result2:
                        print(service.uuid)
                else:
                    print(service.uuid)
                    print("Service must be redeployed to have its configuration changes applied.")
                    print("To redeploy execute: $ docker-cloud service redeploy", identifier)
        except Exception as e:
            print(e, file=sys.stderr)
            has_exception = True
    if has_exception:
        sys.exit(EXCEPTION_EXIT_CODE)
