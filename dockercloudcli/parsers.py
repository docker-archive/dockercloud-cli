import argparse


def add_login_parser(subparsers):
    # docker-cloud login
    login_parser = subparsers.add_parser('login',
                                         help='Please use "docker login" to log into Docker Cloud',
                                         description='Please use "docker login" to log into Docker Cloud')


def add_event_parser(subparsers):
    # docker-cloud event
    subparsers.add_parser('event', help='Get real time Docker Cloud events',
                          description='Get real time Docker Cloud events')


def add_push_parser(subparsers):
    # docker-cloud push
    push_parser = subparsers.add_parser('push', help='Deprecated. Please use "docker push" instead',
                                        description='Deprecated. Please use "docker push" instead')
    push_parser.add_argument('name', help='name of the image to push')
    push_parser.add_argument('--public', help='push image to public registry', action='store_true')


def add_run_parser(subparsers):
    # docker-cloud run
    run_parser = subparsers.add_parser('run', help='Create and run a new service',
                                       description='Create and run a new service', )
    run_parser.add_argument('image', help='the name of the image used to deploy this service')
    run_parser.add_argument('-n', '--name', help='a human-readable name for the service '
                                                 '(default: image_tag without namespace)')
    run_parser.add_argument('--cpushares', help='Relative weight for CPU Shares', type=int)
    run_parser.add_argument('--memory', help='RAM memory hard limit in MB', type=int)
    run_parser.add_argument('--privileged', help='Give extended privileges to this container', action='store_true')
    run_parser.add_argument('-t', '--target-num-containers',
                            help='the number of containers to run for this service (default: 1)', type=int)
    run_parser.add_argument('-r', '--run-command',
                            help='the command used to start the service containers '
                                 '(default: as defined in the image)')
    run_parser.add_argument('--entrypoint',
                            help='the command prefix used to start the service containers '
                                 '(default: as defined in the image)')
    run_parser.add_argument('-p', '--publish', help="Publish a container's port to the host. "
                                                    "Format: [hostPort:]containerPort[/protocol], i.e. \"80:80/tcp\"",
                            action='append')
    run_parser.add_argument('--expose', help='Expose a port from the container without publishing it to your host',
                            action='append', type=int)
    run_parser.add_argument('-e', '--env',
                            help='set environment variables i.e. "ENVVAR=foo" '
                                 '(default: as defined in the image, plus any link- or role-generated variables)',
                            action='append')
    run_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                            action='append')
    run_parser.add_argument('--tag', help="the tag name being added to the service", action='append')
    run_parser.add_argument('--link-service',
                            help="Add link to another service (name:alias) or (uuid:alias)", action='append')
    run_parser.add_argument('--autodestroy', help='whether the containers should be terminated if '
                                                  'they stop (default: OFF)',
                            choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    run_parser.add_argument('--autoredeploy', help="whether the containers should be auto redeployed.",
                            action='store_true')
    run_parser.add_argument('--autorestart', help='whether the containers should be restarted if they stop '
                                                  '(default: OFF)', choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    run_parser.add_argument('--role', help='Docker Cloud API roles to grant the service, '
                                           'i.e. "global" (default: none, possible values: "global")', action='append')
    run_parser.add_argument('--sequential', help='whether the containers should be launched and scaled sequentially',
                            action='store_true')
    run_parser.add_argument('-v', '--volume', help='Bind mount a volume (e.g., from the host: -v /host:/container, '
                                                   'from Docker: -v /container)', action='append')
    run_parser.add_argument('--volumes-from', help='Mount volumes from the specified service(s)', action='append')
    run_parser.add_argument('--deployment-strategy', help='Container distribution strategy among nodes',
                            choices=['EMPTIEST_NODE', 'HIGH_AVAILABILITY', 'EVERY_NODE'])
    run_parser.add_argument('--sync', help='block the command until the async operation has finished',
                            action='store_true')
    run_parser.add_argument('--net', help='Set the Network mode for the container')
    run_parser.add_argument('--pid', help="PID namespace to use")


def add_up_parser(subparsers):
    # docker-cloud up
    up_parser = subparsers.add_parser('up', help='Create and deploy a stack',
                                      description='Create and deploy a stack')
    up_parser.add_argument('-n', '--name', help='The name of the stack, which will be shown in Docker Cloud')
    up_parser.add_argument('-f', '--file', help="the name of the Stackfile", action='append')
    up_parser.add_argument('--sync', help='block the command until the async operation has finished',
                           action='store_true')


def add_exec_parser(subparsers):
    # docker-cloud exec
    exec_parser = subparsers.add_parser('exec', help='Run a command in a running container',
                                        description='Run a command in a running container')
    exec_parser.add_argument('identifier', help="container's UUID (either long or short) or name")
    exec_parser.add_argument('command', help="the command to run (default: sh)", nargs=argparse.REMAINDER)


def add_action_parser(subparsers):
    # docker-cloud action
    action_parser = subparsers.add_parser('action', help='Action-related operations',
                                          description='Action-related operations')
    action_subparser = action_parser.add_subparsers(title='Docker Cloud action commands', dest='subcmd')

    # docker-cloud action cancel
    inspect_parser = action_subparser.add_parser('cancel', help="Cancel an action in Pending or In progress state",
                                                 description="Cancels an action in Pending or In progress state")
    inspect_parser.add_argument('identifier', help="action's UUID (either long or short)", nargs='+')

    # docker-cloud action inspect
    inspect_parser = action_subparser.add_parser('inspect', help="Get all details from an action",
                                                 description="Get all details from an action")
    inspect_parser.add_argument('identifier', help="action's UUID (either long or short)", nargs='+')

    # docker-cloud action logs
    logs_parser = action_subparser.add_parser('logs', help='Get logs from an action',
                                              description='Get logs from an action')
    logs_parser.add_argument('identifier', help="action's UUID (either long or short)", nargs='+')
    logs_parser.add_argument('-f', '--follow', help='follow log output', action='store_true')
    logs_parser.add_argument('-t', '--tail', help='Output the specified number of lines at the end of logs '
                                                  '(defaults: 300)', type=int)
    # docker-cloud action ls
    list_parser = action_subparser.add_parser('ls', help='List actions', description='List actions')
    list_parser.add_argument('-q', '--quiet', help='print only action uuid', action='store_true')
    list_parser.add_argument('-l', '--last', help='Output the last number of actions (default:25)', type=int)

    # docker-cloud action retry
    inspect_parser = action_subparser.add_parser('retry', help="Retries an action in Success, Failed or Canceled state",
                                                 description="Retries an action in Success, Failed or Canceled state")
    inspect_parser.add_argument('identifier', help="action's UUID (either long or short)", nargs='+')


def add_service_parser(subparsers):
    # docker-cloud service
    service_parser = subparsers.add_parser('service', help='Service-related operations',
                                           description='Service-related operations')
    service_subparser = service_parser.add_subparsers(title='Docker Cloud service commands', dest='subcmd')

    # docker-cloud service run
    create_parser = service_subparser.add_parser('create', help='Create a new service',
                                                 description='Create a new service', )
    create_parser.add_argument('image', help='the name of the image used to deploy this service')
    create_parser.add_argument('-n', '--name', help='a human-readable name for the service '
                                                    '(default: image_tag without namespace)')
    create_parser.add_argument('--cpushares', help='Relative weight for CPU Shares', type=int)
    create_parser.add_argument('--memory', help='RAM memory hard limit in MB', type=int)
    create_parser.add_argument('--privileged', help='Give extended privileges to this container', action='store_true')
    create_parser.add_argument('-t', '--target-num-containers',
                               help='the number of containers to run for this service (default: 1)', type=int)
    create_parser.add_argument('-r', '--run-command',
                               help='the command used to start the service containers '
                                    '(default: as defined in the image)')
    create_parser.add_argument('--entrypoint',
                               help='the command prefix used to start the service containers '
                                    '(default: as defined in the image)')
    create_parser.add_argument('-p', '--publish', help="Publish a container's port to the host. "
                                                       "Format: [hostPort:]containerPort[/protocol], i.e. '80:80/tcp'",
                               action='append')
    create_parser.add_argument('--expose', help='Expose a port from the container without publishing it to your host',
                               action='append', type=int)
    create_parser.add_argument('-e', '--env',
                               help='set environment variables i.e. "ENVVAR=foo" '
                                    '(default: as defined in the image, plus any link- or role-generated variables)',
                               action='append')
    create_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                               action='append')
    create_parser.add_argument('--tag', help="the tag name being added to the service", action='append')
    create_parser.add_argument('--link-service',
                               help="Add link to another service (name:alias) or (uuid:alias)", action='append')
    create_parser.add_argument('--autodestroy', help='whether the containers should be terminated if '
                                                     'they stop (default: OFF)',
                               choices=['OFF', 'ON_SUCCESS', 'ALWAYS'])
    create_parser.add_argument('--autoredeploy', help="whether the containers should be auto redeployed.",
                               action='store_true')
    create_parser.add_argument('--autorestart', help='whether the containers should be restarted if they stop '
                                                     '(default: OFF)', choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    create_parser.add_argument('--role', help='Docker Cloud API roles to grant the service, '
                                              'i.e. "global" (default: none, possible values: "global")',
                               action='append')
    create_parser.add_argument('--sequential', help='whether the containers should be launched and scaled sequentially',
                               action='store_true')
    create_parser.add_argument('-v', '--volume', help='Bind mount a volume (e.g., from the host: -v /host:/container, '
                                                      'from Docker: -v /container)', action='append')
    create_parser.add_argument('--volumes-from', help='Mount volumes from the specified service(s)', action='append')

    create_parser.add_argument('--deployment-strategy', help='Container distribution strategy among nodes',
                               choices=['EMPTIEST_NODE', 'HIGH_AVAILABILITY', 'EVERY_NODE'])
    create_parser.add_argument('--sync', help='block the command until the async operation has finished',
                               action='store_true')
    create_parser.add_argument('--net', help='Set the Network mode for the container')
    create_parser.add_argument('--pid', help="PID namespace to use")

    # docker-cloud service env
    env_parser = service_subparser.add_parser('env', help="Service environment variables related operations",
                                              description="Service environment variables related operations")
    env_subparser = env_parser.add_subparsers(title='Docker Cloud service env commands', dest='envsubcmd')

    # docker-cloud service env add
    env_add_parser = env_subparser.add_parser('add', help='Add new environment variables',
                                              description='Add new environment variables')
    env_add_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                nargs='+')
    env_add_parser.add_argument('-e', '--env',
                                help='set environment variables i.e. "ENVVAR=foo" '
                                     '(default: as defined in the image, plus any link- or role-generated variables)',
                                action='append')
    env_add_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                                action='append')
    env_add_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                action='store_true')
    env_add_parser.add_argument('--redeploy', help="redeploy service with new configuration after set command",
                                action='store_true')

    # docker-cloud service env ls
    env_list_parser = env_subparser.add_parser('ls', help='list all environment variables',
                                               description='list all environment variables')
    env_list_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]")
    env_list_parser.add_argument('-q', '--quiet', help='print only key value pair', action='store_true')
    env_list_parser.add_argument('--user', help='show only user defined environment variables', action='store_true')
    env_list_parser.add_argument('--image', help='show only image defined environment variables', action='store_true')
    env_list_parser.add_argument('--dockercloud', help='show only Docker Cloud defined environment variables',
                                 action='store_true')

    # docker-cloud service env remove
    env_remove_parser = env_subparser.add_parser('rm', help='Remove existing environment variables',
                                                 description='Remove existing environment variables')
    env_remove_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                   nargs='+')
    env_remove_parser.add_argument('-n', '--name', help='names of the environments to remove', action='append')
    env_remove_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                   action='store_true')
    env_remove_parser.add_argument('--redeploy', help="redeploy service with new configuration after set command",
                                   action='store_true')

    # docker-cloud service env set
    env_set_parser = env_subparser.add_parser('set', help='Replace existing environment variables with new ones',
                                              description='Replace existing environment variables with new ones')
    env_set_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                nargs='+')
    env_set_parser.add_argument('-e', '--env',
                                help='set environment variables i.e. "ENVVAR=foo" '
                                     '(default: as defined in the image, plus any link- or role-generated variables)',
                                action='append')
    env_set_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                                action='append')
    env_set_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                action='store_true')
    env_set_parser.add_argument('--redeploy', help="redeploy service with new configuration after set command",
                                action='store_true')

    # docker-cloud service env update
    env_update_parser = env_subparser.add_parser('update', help='Update existing environment variables with new values',
                                                 description='Update existing environment variables with new values')
    env_update_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                   nargs='+')
    env_update_parser.add_argument('-e', '--env',
                                   help='set environment variables i.e. "ENVVAR=foo" (default: '
                                        'as defined in the image, plus any link- or role-generated variables)',
                                   action='append')
    env_update_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                                   action='append')
    env_update_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                   action='store_true')
    env_update_parser.add_argument('--redeploy', help="redeploy service with new configuration after set command",
                                   action='store_true')

    # docker-cloud service inspect
    inspect_parser = service_subparser.add_parser('inspect', help="Get all details from a service",
                                                  description="Get all details from a service")
    inspect_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                nargs='+')

    # docker-cloud service logs
    logs_parser = service_subparser.add_parser('logs', help='Get logs from a service',
                                               description='Get logs from a service')
    logs_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]", nargs='+')
    logs_parser.add_argument('-f', '--follow', help='follow log output', action='store_true')
    logs_parser.add_argument('-t', '--tail', help='Output the specified number of lines at the end of logs '
                                                  '(defaults: 300)', type=int)

    # docker-cloud service ps
    ps_parser = service_subparser.add_parser('ps', help='List services', description='List services')
    ps_parser.add_argument('-q', '--quiet', help='print only long UUIDs', action='store_true')
    ps_parser.add_argument('-s', '--status', help='filter services by status',
                           choices=['Init', 'Stopped', 'Starting', 'Running', 'Stopping', 'Terminating', 'Terminated',
                                    'Scaling', 'Partly running', 'Not running', 'Redeploying'])
    ps_parser.add_argument('--stack', help="filter services by stack (UUID either long or short, or name)")

    # docker-cloud service redeploy
    redeploy_parser = service_subparser.add_parser('redeploy', help='Redeploy a running service',
                                                   description='Redeploy a running service')
    redeploy_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                 nargs='+')
    redeploy_parser.add_argument('--not-reuse-volumes', help="do not reuse volumes in redeployment",
                                 action='store_true')
    redeploy_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                 action='store_true')

    # docker-cloud service run
    run_parser = service_subparser.add_parser('run', help='Create and run a new service',
                                              description='Create and run a new service', )
    run_parser.add_argument('image', help='the name of the image used to deploy this service')
    run_parser.add_argument('-n', '--name', help='a human-readable name for the service '
                                                 '(default: image_tag without namespace)')
    run_parser.add_argument('--cpushares', help='Relative weight for CPU Shares', type=int)
    run_parser.add_argument('--memory', help='RAM memory hard limit in MB', type=int)
    run_parser.add_argument('--privileged', help='Give extended privileges to this container', action='store_true')
    run_parser.add_argument('-t', '--target-num-containers',
                            help='the number of containers to run for this service (default: 1)', type=int)
    run_parser.add_argument('-r', '--run-command',
                            help='the command used to start the service containers '
                                 '(default: as defined in the image)')
    run_parser.add_argument('--entrypoint',
                            help='the command prefix used to start the service containers '
                                 '(default: as defined in the image)')
    run_parser.add_argument('-p', '--publish', help="Publish a container's port to the host. "
                                                    "Format: [hostPort:]containerPort[/protocol], i.e. \"80:80/tcp\"",
                            action='append')
    run_parser.add_argument('--expose', help='Expose a port from the container without publishing it to your host',
                            action='append', type=int)
    run_parser.add_argument('-e', '--env',
                            help='set environment variables i.e. "ENVVAR=foo" '
                                 '(default: as defined in the image, plus any link- or role-generated variables)',
                            action='append')
    run_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                            action='append')
    run_parser.add_argument('--tag', help="the tag name being added to the service", action='append')
    run_parser.add_argument('--link-service',
                            help="Add link to another service (name:alias) or (uuid:alias)", action='append')
    run_parser.add_argument('--autodestroy', help='whether the containers should be terminated if '
                                                  'they stop (default: OFF)',
                            choices=['OFF', 'ON_SUCCESS', 'ALWAYS'])
    run_parser.add_argument('--autoredeploy', help="whether the containers should be auto redeployed.",
                            action='store_true')
    run_parser.add_argument('--autorestart', help='whether the containers should be restarted if they stop '
                                                  '(default: OFF)', choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    run_parser.add_argument('--role', help='Docker Cloud API roles to grant the service, '
                                           'i.e. "global" (default: none, possible values: "global")', action='append')
    run_parser.add_argument('--sequential', help='whether the containers should be launched and scaled sequentially',
                            action='store_true')
    run_parser.add_argument('-v', '--volume', help='Bind mount a volume (e.g., from the host: -v /host:/container, '
                                                   'from Docker: -v /container)', action='append')
    run_parser.add_argument('--volumes-from', help='Mount volumes from the specified service(s)', action='append')
    run_parser.add_argument('--deployment-strategy', help='Container distribution strategy among nodes',
                            choices=['EMPTIEST_NODE', 'HIGH_AVAILABILITY', 'EVERY_NODE'])
    run_parser.add_argument('--sync', help='block the command until the async operation has finished',
                            action='store_true')
    run_parser.add_argument('--net', help='Set the Network mode for the container')
    run_parser.add_argument('--pid', help="PID namespace to use")

    # docker-cloud service scale
    scale_parser = service_subparser.add_parser('scale', help='Scale a running service',
                                                description='Scale a running service', )
    scale_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                              nargs='+')
    scale_parser.add_argument("target_num_containers", metavar="target-num-containers",
                              help="target number of containers to scale this service to", type=int)
    scale_parser.add_argument('--sync', help='block the command until the async operation has finished',
                              action='store_true')

    # docker-cloud service set
    set_parser = service_subparser.add_parser('set', help='Change and replace the existing service properties',
                                              description='Change service properties.'
                                                          ' This command REPLACES the existing properties.')
    set_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]", nargs='+')
    set_parser.add_argument('--image', help='the name of the image used to deploy this service')
    set_parser.add_argument('--cpushares', help='Relative weight for CPU Shares', type=int)
    set_parser.add_argument('--memory', help='RAM memory hard limit in MB', type=int)
    set_parser.add_argument('--privileged', help='Give extended privileges to this container',
                            dest='privileged', action='store_true')
    set_parser.add_argument('--no-privileged', help='Reclaim extended privileges from this container',
                            dest='privileged', action='store_false')
    set_parser.set_defaults(privileged=None)
    set_parser.add_argument('-t', '--target-num-containers',
                            help='the number of containers to run for this service', type=int)
    set_parser.add_argument('-r', '--run-command',
                            help='the command used to start the service containers '
                                 '(default: as defined in the image)')
    set_parser.add_argument('--entrypoint',
                            help='the command prefix used to start the service containers '
                                 '(default: as defined in the image)')
    set_parser.add_argument('-p', '--publish', help="Publish a container's port to the host. "
                                                    "Format: [hostPort:]containerPort[/protocol], i.e. \"80:80/tcp\"",
                            action='append')
    set_parser.add_argument('--expose', help='Expose a port from the container without publishing it to your host',
                            action='append', type=int)
    set_parser.add_argument('-e', '--env',
                            help='set environment variables i.e. "ENVVAR=foo" '
                                 '(default: as defined in the image, plus any link- or role-generated variables)',
                            action='append')
    set_parser.add_argument('--env-file', help='read in a line delimited file of environment variables',
                            action='append')
    set_parser.add_argument('--tag', help="the tag name being added to the service", action='append')
    set_parser.add_argument('--link-service',
                            help="Add link to another service (name:alias) or (uuid:alias)", action='append')
    set_parser.add_argument('--autodestroy', help='whether the containers should be terminated if '
                                                  'they stop (default: OFF)',
                            choices=['OFF', 'ON_SUCCESS', 'ALWAYS'])
    set_parser.add_argument('--autoredeploy', help="set the containers to be auto redeployed",
                            dest='autoredeploy', action='store_true')
    set_parser.add_argument('--no-autoredeploy', help="set the containers not to be auto redeployed",
                            dest='autoredeploy', action='store_false')
    set_parser.set_defaults(autoredeploy=None)
    set_parser.add_argument('--autorestart', help='whether the containers should be restarted if they stop '
                                                  '(default: OFF)', choices=['OFF', 'ON_FAILURE', 'ALWAYS'])
    set_parser.add_argument('--role', help='Docker Cloud API roles to grant the service, '
                                           'i.e. "global" (default: none, possible values: "global")', action='append')
    set_parser.add_argument('--sequential',
                            help='set the containers to be launched and scaled sequentially',
                            dest='sequential', action='store_true')
    set_parser.add_argument('--no-sequential',
                            help='set the containers not to be launched and scaled sequentially',
                            dest='sequential', action='store_false')
    set_parser.set_defaults(sequential=None)
    set_parser.add_argument('--redeploy', help="redeploy service with new configuration after set command",
                            action='store_true')
    set_parser.add_argument('-v', '--volume', help='Bind mount a volume (e.g., from the host: -v /host:/container, '
                                                   'from Docker: -v /container)', action='append')
    set_parser.add_argument('--volumes-from', help='Mount volumes from the specified service(s)', action='append')
    set_parser.add_argument('--deployment-strategy', help='Container distribution strategy among nodes',
                            choices=['EMPTIEST_NODE', 'HIGH_AVAILABILITY', 'EVERY_NODE'])
    set_parser.add_argument('--sync', help='block the command until the async operation has finished',
                            action='store_true')
    set_parser.add_argument('--net', help='Set the Network mode for the container')
    set_parser.add_argument('--pid', help="PID namespace to use")

    # docker-cloud service start
    start_parser = service_subparser.add_parser('start', help='Start a stopped service',
                                                description='Start a stopped service')
    start_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                              nargs='+')
    start_parser.add_argument('--sync', help='block the command until the async operation has finished',
                              action='store_true')

    # docker-cloud service stop
    stop_parser = service_subparser.add_parser('stop', help='Stop a running service',
                                               description='Stop a running service')
    stop_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]", nargs='+')
    stop_parser.add_argument('--sync', help='block the command until the async operation has finished',
                             action='store_true')

    # docker-cloud service terminate
    terminate_parser = service_subparser.add_parser('terminate', help='Terminate a service',
                                                    description='Terminate a service')
    terminate_parser.add_argument('identifier', help="service's UUID (either long or short) or name[.stack_name]",
                                  nargs='+')
    terminate_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                  action='store_true')


def add_container_parser(subparsers):
    # docker-cloud container
    container_parser = subparsers.add_parser('container', help='Container-related operations',
                                             description='Container-related operations')
    container_subparser = container_parser.add_subparsers(title='Docker Cloud container commands', dest='subcmd')

    # docker-cloud container exec
    exec_parser = container_subparser.add_parser('exec', help='Run a command in a running container',
                                                 description='Run a command in a running container')
    exec_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]")
    exec_parser.add_argument('command', help="the command to run (default: sh)", nargs=argparse.REMAINDER)

    # docker-cloud container inspect
    inspect_parser = container_subparser.add_parser('inspect', help='Inspect a container',
                                                    description='Inspect a container')
    inspect_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]",
                                nargs='+')

    # docker-cloud container logs
    logs_parser = container_subparser.add_parser('logs', help='Get logs from a container',
                                                 description='Get logs from a container')
    logs_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]",
                             nargs='+')
    logs_parser.add_argument('-f', '--follow', help='follow log output', action='store_true')
    logs_parser.add_argument('-t', '--tail', help='Output the specified number of lines at the end of logs '
                                                  '(defaults: 300)', type=int)

    redeploy_parser = container_subparser.add_parser('redeploy', help='Redeploy a running container',
                                                     description='Redeploy a running container')
    redeploy_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]",
                                 nargs='+')
    redeploy_parser.add_argument('--not-reuse-volumes', help="do not reuse volumes in redeployment",
                                 action='store_true')
    redeploy_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                 action='store_true')

    # docker-cloud container ps
    ps_parser = container_subparser.add_parser('ps', help='List containers', description='List containers')
    ps_parser.add_argument('-q', '--quiet', help='print only long UUIDs', action='store_true')
    ps_parser.add_argument('-s', '--status', help='filter containers by status',
                           choices=['Init', 'Stopped', 'Starting', 'Running', 'Stopping', 'Terminating', 'Terminated'])
    ps_parser.add_argument('--service', help="filter containers by service (UUID either long or short, or name)")
    ps_parser.add_argument('--no-trunc', help="don't truncate output", action='store_true')

    # docker-cloud container start
    start_parser = container_subparser.add_parser('start', help='Start a container', description='Start a container')
    start_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]",
                              nargs='+')
    start_parser.add_argument('--sync', help='block the command until the async operation has finished',
                              action='store_true')

    # docker-cloud container stop
    stop_parser = container_subparser.add_parser('stop', help='Stop a container', description='Stop a container')
    stop_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]",
                             nargs='+')
    stop_parser.add_argument('--sync', help='block the command until the async operation has finished',
                             action='store_true')

    # docker-cloud container terminate
    terminate_parser = container_subparser.add_parser('terminate', help='Terminate a container',
                                                      description='Terminate a container')
    terminate_parser.add_argument('identifier', help="container's UUID (either long or short) or name[.stack_name]",
                                  nargs='+')
    terminate_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                  action='store_true')


def add_repository_parser(subparsers):
    # docker-cloud repository
    repository_parser = subparsers.add_parser('repository', help='Repository-related operations',
                                              description='Repository-related operations')
    repository_subparser = repository_parser.add_subparsers(title='Docker Cloud repository commands', dest='subcmd')

    # docker-cloud repository ls
    list_parser = repository_subparser.add_parser('ls', help="List all registered external repositories",
                                                  description="List all registered external repositories")
    list_parser.add_argument('-q', '--quiet', help='print only repository names', action='store_true')

    # docker-cloud repository inspect
    inspect_parser = repository_subparser.add_parser('inspect', help='Inspect an external repository',
                                                     description='Inspect an external repository')
    inspect_parser.add_argument('identifier', help="repository name", nargs='+')

    # docker-cloud repository register
    register_parser = repository_subparser.add_parser('register',
                                                      help='Register an external repository in Docker Cloud',
                                                      description='Register an external repository in Docker Cloud')
    register_parser.add_argument('repository_name', help='full repository name, i.e. quay.io/docker/test-repo')
    register_parser.add_argument('-u', '--username', help='username to authenticate with the external registry')
    register_parser.add_argument('-p', '--password', help='password to authenticate with the external registry')

    # docker-cloud repository rm
    rm_parser = repository_subparser.add_parser('rm', help='Remove an external repository from Docker Cloud',
                                                description='Remove an external repository from Docker Cloud')
    rm_parser.add_argument('repository_name', help='full repository name, i.e. quay.io/docker/test-repo', nargs='+')

    # docker-cloud repository update
    update_parser = repository_subparser.add_parser('update', help='Update a registered repository in Docker Cloud',
                                                    description='Update a registered repository in Docker Cloud')
    update_parser.add_argument("repository_name", help="full repository name, i.e. quay.io/docker/test-repo", nargs="+")
    update_parser.add_argument('-u', '--username', help='new username to authenticate with the external registry')
    update_parser.add_argument('-p', '--password', help='new password to authenticate with the external registry')


def add_node_parser(subparsers):
    # docker-cloud node
    node_parser = subparsers.add_parser('node', help='Node-related operations', description='Node-related operations')
    node_subparser = node_parser.add_subparsers(title='Docker Cloud node commands', dest='subcmd')

    # docker-cloud byo
    node_subparser.add_parser('byo', help='Instructions on how to Bring Your Own server to Docker Cloud',
                              description='Instructions on how to Bring Your Own server to Docker Cloud')

    # docker-cloud node inspect
    inspect_parser = node_subparser.add_parser('inspect', help='Inspect a node', description='Inspect a node')
    inspect_parser.add_argument('identifier', help="node's UUID (either long or short)", nargs='+')

    # docker-cloud node ls
    list_parser = node_subparser.add_parser('ls', help='List nodes', description='List nodes')
    list_parser.add_argument('-q', '--quiet', help='print only node uuid', action='store_true')

    # docker-cloud node rm
    rm_parser = node_subparser.add_parser('rm', help='Remove a node', description='Remove a container')
    rm_parser.add_argument('identifier', help="node's UUID (either long or short)", nargs='+')
    rm_parser.add_argument('--sync', help='block the command until the async operation has finished',
                           action='store_true')

    # docker-cloud node upgrade
    upgrade_parser = node_subparser.add_parser('upgrade', help='Upgrade docker daemon on the node',
                                               description='Upgrade docker daemon to the latest version on the node')
    upgrade_parser.add_argument('identifier', help="node's UUID (either long or short)", nargs='+')
    upgrade_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                action='store_true')


def add_nodecluster_parser(subparsers):
    # docker-cloud nodecluster
    nodecluster_parser = subparsers.add_parser('nodecluster', help='NodeCluster-related operations',
                                               description='NodeCluster-related operations')
    nodecluster_subparser = nodecluster_parser.add_subparsers(title='Docker Cloud node commands', dest='subcmd')

    # docker-cloud nodecluster az
    az_parser = nodecluster_subparser.add_parser('az', help='Show all available availability zones')
    az_parser.add_argument('-q', '--quiet', help='print only availability zone name', action='store_true')

    # docker-cloud nodecluster create
    create_parser = nodecluster_subparser.add_parser('create', help='Create a nodecluster',
                                                     description='Create a nodecluster')
    create_parser.add_argument('-t', '--target-num-nodes',
                               help='the target number of nodes to run for this cluster (default: 1)', type=int)
    create_parser.add_argument('name', help='name of the node cluster to create')
    create_parser.add_argument('provider', help='name of the provider')
    create_parser.add_argument('region', help='name of the region')
    create_parser.add_argument('nodetype', help='name of the node type')
    create_parser.add_argument('--sync', help='block the command until the async operation has finished',
                               action='store_true')
    create_parser.add_argument('--disk', help="Disk size of node in GB(Default:60). "
                                              "The available value varies depending on the providers")
    create_parser.add_argument('--tag', help="set the tag of the node cluster", action='append')
    create_parser.add_argument('--aws-vpc-id', help='aws provider option: vpc id')
    create_parser.add_argument('--aws-vpc-subnet', help="aws provider option: vpc subnet",
                               action='append')
    create_parser.add_argument('--aws-vpc-security-group', help="aws provider option: vpc security group",
                               action='append')
    create_parser.add_argument('--aws-iam-instance-profile-name',
                               help='aws provider option: instance profile name for the iam')

    # docker-cloud nodecluster inspect
    inspect_parser = nodecluster_subparser.add_parser('inspect', help='Inspect a nodecluster',
                                                      description='Inspect a nodecluster')
    inspect_parser.add_argument('identifier', help="node's UUID (either long or short)", nargs='+')

    # docker-cloud nodecluster ls
    list_parser = nodecluster_subparser.add_parser('ls', help='List node clusters', description='List node clusters')
    list_parser.add_argument('-q', '--quiet', help='print only node uuid', action='store_true')

    # docker-cloud nodecluster nodetype
    nodetype_parser = nodecluster_subparser.add_parser('nodetype', help='Show all available types')
    nodetype_parser.add_argument('-p', '--provider', help="filtered by provider name (e.g. digitalocean)")
    nodetype_parser.add_argument('-r', '--region', help="filtered by region name (e.g. ams1)")

    # docker-cloud nodecluster provider
    provider_parser = nodecluster_subparser.add_parser('provider', help='Show all available infrastructure providers',
                                                       description='Show all available infrastructure providers')
    provider_parser.add_argument('-q', '--quiet', help='print only provider name', action='store_true')

    # docker-cloud nodecluster region
    region_parser = nodecluster_subparser.add_parser('region', help='Show all available regions')
    region_parser.add_argument('-p', '--provider', help="filtered by provider name (e.g. digitalocean)")

    # docker-cloud nodecluster rm
    rm_parser = nodecluster_subparser.add_parser('rm', help='Remove node clusters', description='Remove node clusters')
    rm_parser.add_argument('identifier', help="node's UUID (either long or short)", nargs='+')
    rm_parser.add_argument('--sync', help='block the command until the async operation has finished',
                           action='store_true')

    # docker-cloud nodecluster scale
    scale_parser = nodecluster_subparser.add_parser('scale', help='Scale a running node cluster',
                                                    description='Scale a running node cluster', )
    scale_parser.add_argument('identifier', help="node cluster's UUID (either long or short) or name", nargs='+')
    scale_parser.add_argument("target_num_nodes", metavar="target-num-nodes",
                              help="target number of nodes to scale this node cluster to", type=int)
    scale_parser.add_argument('--sync', help='block the command until the async operation has finished',
                              action='store_true')


def add_tag_parser(subparsers):
    # docker-cloud tag
    tag_parser = subparsers.add_parser('tag', help='Tag-related operations', description='Tag-related operations')
    tag_subparser = tag_parser.add_subparsers(title='Docker Cloud tag commands', dest='subcmd')

    # docker-cloud tag add
    add_parser = tag_subparser.add_parser('add', help='Add tags to services, nodes or nodeclusters',
                                          description='Add tags to services, nodes or nodeclusters')
    add_parser.add_argument('-t', '--tag', help="name of the tag", action='append', required=True)
    add_parser.add_argument('identifier', help="UUID or name of services, nodes or nodeclusters", nargs='+')

    # docker-cloud tag ls
    list_parser = tag_subparser.add_parser('ls', help='List all tags associated with services, nodes or nodeclusters',
                                           description='List all tags associated with services, nodes or nodeclusters')
    list_parser.add_argument('identifier', help="UUID or name of services, nodes or nodeclusters", nargs='+')
    list_parser.add_argument('-q', '--quiet', help='print only tag names', action='store_true')

    # docker-cloud tag rm
    rm_parser = tag_subparser.add_parser('rm', help='Remove tags from services, nodes or nodeclusters',
                                         description='Remove tags from services, nodes or nodeclusters')
    rm_parser.add_argument('-t', '--tag', help="name of the tag", action='append', required=True)
    rm_parser.add_argument('identifier', help="UUID or name of services, nodes or nodeclusters", nargs='+')

    # docker-cloud tag set
    set_parser = tag_subparser.add_parser('set', help='Set tags from services, nodes or nodeclusters, '
                                                      'overwriting existing tags',
                                          description='Set tags from services, nodes or nodeclusters. '
                                                      'This will remove all the existing tags')
    set_parser.add_argument('-t', '--tag', help="name of the tag", action='append', required=True)
    set_parser.add_argument('identifier', help="UUID or name of services, nodes or nodeclusters", nargs='+')


def add_trigger_parser(subparsers):
    # docker-cloud trigger
    trigger_parser = subparsers.add_parser('trigger', help='Trigger-related operations',
                                           description='Trigger-related operations')
    trigger_subparser = trigger_parser.add_subparsers(title='Docker Cloud trigger commands', dest='subcmd')

    # docker-cloud trigger create
    create_parser = trigger_subparser.add_parser('create', help='Create trigger to services',
                                                 description='Create trigger to services')
    create_parser.add_argument('-n', '--name', help="name of the trigger (optional)")
    create_parser.add_argument('-o', '--operation', help="operation of the trigger(default:redeploy)")
    create_parser.add_argument('identifier', help="UUID or name of services")

    # docker-cloud trigger ls
    list_parser = trigger_subparser.add_parser('ls', help='List all trigger associated with services',
                                               description='List all triggers associated with services')
    list_parser.add_argument('identifier', help="UUID or name of services")
    list_parser.add_argument('-q', '--quiet', help='print only trigger uuid', action='store_true')

    # docker-cloud trigger delete
    rm_parser = trigger_subparser.add_parser('rm', help='Remove trigger from a service',
                                             description='Remove trigger from a service')
    rm_parser.add_argument('identifier', help="UUID or name of services")
    rm_parser.add_argument('trigger', help="UUID or name of the trigger", nargs='+')


def add_stack_parser(subparsers):
    # docker-cloud stack
    stack_parser = subparsers.add_parser('stack', help='Stack-related operations',
                                         description='Stack-related operations')
    stack_subparser = stack_parser.add_subparsers(title='Docker Cloud stack commands', dest='subcmd')

    # docker-cloud stack create
    create_parser = stack_subparser.add_parser('create', help='Create a new stack without deploying',
                                               description='Create a new stack without deploying')
    create_parser.add_argument('-n', '--name', help='The name of the stack, which wil be shown in Docker Cloud')
    create_parser.add_argument('-f', '--file', help="the name of the Stackfile", action='append')
    create_parser.add_argument('--sync', help='block the command until the async operation has finished',
                               action='store_true')

    # docker-cloud stack export
    export_parser = stack_subparser.add_parser('export', help='Export the stack from Docker Cloud',
                                               description='Export the stack from Docker Cloud')
    export_parser.add_argument('identifier', help='UUID or name of the stack')
    export_parser.add_argument('-f', '--file', help="the name of the file to export to")

    # docker-cloud stack inspect
    inspect_parser = stack_subparser.add_parser('inspect', help='Inspect a stack', description='Inspect a stack')
    inspect_parser.add_argument('identifier', help="stack's UUID (either long or short) or name", nargs='+')

    # docker-cloud stack ls
    list_parser = stack_subparser.add_parser('ls', help='List stacks', description='List stacks')
    list_parser.add_argument('-q', '--quiet', help='print only long UUIDs', action='store_true')

    # docker-cloud stack redeploy
    redeploy_parser = stack_subparser.add_parser('redeploy', help='Redeploy a running stack',
                                                 description='Redeploy a running stack')
    redeploy_parser.add_argument('identifier', help="stack's UUID (either long or short) or name", nargs='+')
    redeploy_parser.add_argument('--not-reuse-volumes', help="do not reuse volumes in redeployment",
                                 action='store_true')
    redeploy_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                 action='store_true')

    # docker-cloud stack start
    start_parser = stack_subparser.add_parser('start', help='Start a stack', description='Start a stack')
    start_parser.add_argument('identifier', help="stack's UUID (either long or short) or name", nargs='+')
    start_parser.add_argument('--sync', help='block the command until the async operation has finished',
                              action='store_true')

    # docker-cloud stack stop
    stop_parser = stack_subparser.add_parser('stop', help='Stop a stack', description='Stop a stack')
    stop_parser.add_argument('identifier', help="stack's UUID (either long or short) or name", nargs='+')
    stop_parser.add_argument('--sync', help='block the command until the async operation has finished',
                             action='store_true')

    # docker-cloud stack terminate
    terminate_parser = stack_subparser.add_parser('terminate', help='Terminate a stack',
                                                  description='Terminate a stack')
    terminate_parser.add_argument('identifier', help="stack's UUID (either long or short) or name", nargs='+')
    terminate_parser.add_argument('--sync', help='block the command until the async operation has finished',
                                  action='store_true')

    # docker-cloud stack up
    up_parser = stack_subparser.add_parser('up', help='Create and deploy a stack',
                                           description='Create and deploy a stack')
    up_parser.add_argument('-n', '--name', help='The name of the stack, which will be shown in Docker Cloud')
    up_parser.add_argument('-f', '--file', help="the name of the Stackfile", action='append')
    up_parser.add_argument('--sync', help='block the command until the async operation has finished',
                           action='store_true')

    # docker-cloud stack update
    update_parser = stack_subparser.add_parser('update', help='Update a stack', description='Update a stack')
    update_parser.add_argument('identifier', help="stack's UUID (either long or short) or name")
    update_parser.add_argument('-f', '--file', help="the name of the Stackfile", action='append')
    update_parser.add_argument('--sync', help='block the command until the async operation has finished',
                               action='store_true')
