#!/usr/bin/env python

from resource_management.core.logger import Logger
from resource_management.core.resources import User
from resource_management.core.resources.system import File
from resource_management.core.resources.system import Execute
from resource_management.core.exceptions import ExecutionFailed
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.libraries.functions.get_user_call_output import get_user_call_output


def create_user(params):
    """
    Creates the user required for RabbitMQ.
    """
    Logger.info("Creating user={0} in group={1}".format(params.rabbitmq_user, params.rabbitmq_group))
    User(params.rabbitmq_user, action="create", groups=params.rabbitmq_group)


def service_check(cmd, user, label):
    """
    Executes a SysV service check command that adheres to LSB-compliant
    return codes.  The return codes are interpreted as defined
    by the LSB.

    See http://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/iniscrptact.html
    for more information.

    :param cmd: The service check command to execute.
    :param label: The name of the service.
    """
    Logger.info("Performing service check; cmd={0}, user={1}, label={2}".format(cmd, user, label))
    rc, out, err = get_user_call_output(cmd, user, is_checked_call=False)

    if rc in [1, 2, 3]:
        # if return code in [1, 2, 3], then 'program is not running' or 'program is dead'
        Logger.info("{0} is not running".format(label))
        raise ComponentIsNotRunning()

    elif rc == 0:
        # if return code = 0, then 'program is running or service is OK'
        Logger.info("{0} is running".format(label))

    else:
        # else service state is unknown
        err_msg = "{0} service check failed; cmd '{1}' returned {2}".format(label, cmd, rc)
        Logger.error(err_msg)
        raise ExecutionFailed(err_msg, rc, out, err)


def create_rabbitmq_env(params):
    """
    Creates RabbitMQ Configuration
    """
    Logger.info("Create /etc/rabbitmq/rabbitmq-env.conf file")
    rabbitmq_env = params.config['configurations']['rabbitmq-env']

    content = \
        "# Defaults to rabbit. This can be useful if you want to run more than one node\n" \
        "# Defaults to rabbit. This can be useful if you want to run more than one node\n" \
        "# per machine - RABBITMQ_NODENAME should be unique per erlang-node-and-machine\n" \
        "# combination. See the clustering on a single machine guide for details:\n" \
        "# http://www.rabbitmq.com/clustering.html#single-machine\n" \
        "NODENAME={0}\n" \
        "# By default RabbitMQ will bind to all interfaces, on IPv4 and IPv6 if\n" \
        "# available. Set this if you only want to bind to one network interface or#\n" \
        "# address family.\n" \
        "NODE_IP_ADDRESS={1}\n" \
        "# Defaults to 5672.\n" \
        "NODE_PORT={2}\n" \
        "export RABBITMQ_CONFIG_FILE=\"/etc/rabbitmq/rabbitmq\"\n".format(rabbitmq_env['node_name'],
                                                                          rabbitmq_env['listen_interface'],
                                                                          rabbitmq_env['port'])

    File("/etc/rabbitmq/rabbitmq-env.conf",
         owner=params.rabbitmq_user,
         group=params.rabbitmq_group,
         content=content)


def create_rabbitmq_plugin_conf(params):
    """
    Creates RabbitMQ Extra Configurations
    """
    Logger.info("Create /etc/rabbitmq/rabbitmq.config file")
    rabbitmq_management_port = params.config['configurations']['rabbitmq-management-plugin']['port']

    content = "[\n" \
              "   {{rabbit, []}},\n" \
              "   {{kernel,[]}},\n" \
              "   {{rabbitmq_management,[{{listener, [\n" \
              "		{{port,     {0}}}\n" \
              "   ]}}]}},\n" \
              "   {{rabbitmq_shovel,[{{shovels,[]}}]}},\n" \
              "   {{rabbitmq_stomp,[]}},\n" \
              "   {{rabbitmq_mqtt,[]}},\n" \
              "   {{rabbitmq_amqp1_0,[]}},\n" \
              "   {{rabbitmq_auth_backend_ldap,[]}},\n" \
              "   {{lager, []}}\n" \
              "].".format(rabbitmq_management_port)

    File("/etc/rabbitmq/rabbitmq.config",
         owner=params.rabbitmq_user,
         group=params.rabbitmq_group,
         content=content)


def remove_guest_user():
    """
    Remove guest(default) user of RabbitMQ
    """
    Logger.info("Remove guest user")
    Execute("rabbitmqctl delete_user guest", ignore_failures=True)


def add_admin_user(params):
    """
    Add admin user to RabbitMQ
    """
    admin_username = params.config['configurations']['rabbitmq-env']['admin_username']
    admin_password = params.config['configurations']['rabbitmq-env']['admin_password']
    Logger.info("Add {0} user as administrator to RabbitMQ".format(admin_username))
    Execute("rabbitmqctl add_user {0} {1}".format(admin_username, admin_password), ignore_failures=True)
    Execute("rabbitmqctl change_password {0} {1}".format(admin_username, admin_password), ignore_failures=True)
    Execute("rabbitmqctl set_user_tags {0} administrator".format(admin_username), ignore_failures=True)
    Execute("rabbitmqctl set_permissions -p / {0} \".*\" \".*\" \".*\"".format(admin_username), ignore_failures=True)


def configure_rabbitmq():
    """
    Configure RabbitMQ Server
    """
    import params

    create_rabbitmq_env(params)
    create_rabbitmq_plugin_conf(params)
