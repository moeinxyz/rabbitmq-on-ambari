from rabbitmq_commands import *
from resource_management.core.logger import Logger
from resource_management.libraries.script import Script
from resource_management.core.resources.system import Execute

class RabbitmqServer(Script):
    def install(self, env):
        import params
        env.set_params(params)
        Logger.info("Install RabbitMQ Key")
        Execute("echo \"deb http://dl.bintray.com/rabbitmq-erlang/debian bionic erlang\" | sudo tee /etc/apt/sources.list.d/bintray.erlang.list")
        Execute("apt-get update")
        create_user(params)
        Logger.info("Install RabbitMQ from bintary")
        self.install_packages(env)
        Logger.info("Install rabbitmq-server management panel")
        Execute("sudo rabbitmq-plugins enable rabbitmq_management")
        self.start(env)

    def configure(self, env):
        Logger.info("Configure RabbitMQ Server")
        import params
        env.set_params(params)
        configure_rabbitmq()

    def start(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        Logger.info("Start rabbitmq-server")
        Execute("sudo service rabbitmq-server start")
        remove_guest_user()
        add_admin_user(params)

    def stop(self, env):
        import params
        env.set_params(params)
        Logger.info("Stop rabbitmq-server")
        Execute("sudo service rabbitmq-server stop")

    def status(self, env):
        import params
        env.set_params(params)
        Logger.info("Check rabbitmq-server status")
        service_check(
          cmd="service rabbitmq-server status",
          user=params.rabbitmq_user,
          label="RabbitMQ Server"
        )


if __name__ == "__main__":
    RabbitmqServer().execute()
