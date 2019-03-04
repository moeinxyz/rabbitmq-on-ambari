# RabbitMQ on Ambari
#### Install, configure and monitor single node rabbitmq server on ambari cluster

## Installation

**Run following commands on run own desktop**
```bash
git clone 
cd rabbitmq-on-ambari
tar -cvzf rabbitmq-on-ambari.tar.gz rabbitmq-on-ambari
scp rabbitmq-on-ambari.tar.gz root@your-ambari-master:/tmp/rabbitmq-on-ambari.tar.gz
```

**Connect to your-ambari-master**
```bash
ambari-server stop
ambari-server --install-mpack -mpack=/tmp/rabbitmq-on-ambari.tar.gz -v
ambari-server start

```
**Connect to machine which you have selected to host rabbitmq-server**
It can be you ambari-server machine too!
```bash
wget -O- https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc | sudo apt-key add -
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
```

**You just need browser**
 * connect to your ambari panel
 * add rabbitmq service from ... section
 * follow ui and enjoy rabbitmq on your cluster
 
## After Installation
* This package will remove guest user
* This package will add new user with admin privileges based on your configurations on installation time. You can change admin password on configurations
* This package will install management-plugin by default, you can change its port on configuration or installation process.

## To Do
 * Support clustering
 * Support centos and fedora
 * 
