
FROM registry.access.redhat.com/rhel
MAINTAINER Alex Collins

# add your own red hat user/pass
RUN subscription-manager register --auto-attach --username=USERNAME --password=PASSWORD

# enable the repos we need
RUN subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-optional-rpms

# atomic has a hard dep on docker, so we only need to install the atomic tool
RUN yum -y install atomic git wget tar gcc openssl openssl-devel python-devel libffi-devel pyOpenSSL python-magic python-docker-py

# Update all pkgs 
RUN yum -y update && yum clean all

# grab the code
RUN git clone https://github.com/redhataccess/insights-client.git /var/tmp/insights-client/
RUN git clone https://github.com/ajcollins0/insights-container.git /home/insights-docker/

# copy requirements from RHI/etc/ to /etc/ 
RUN cp -r /var/tmp/insights-client/etc /etc/redhat-access-insights

# delete the empty machine_id file that comes with base RHEL image, this is incompatible with RHI for containers
RUN rm -rf /etc/machine-id 