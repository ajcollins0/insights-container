#!/bin/bash
# Copyright (C) 2016 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

export PS1="(chroot)$ "
export PYTHONPATH="/mnt/opt/python/site-packages"
cd /mnt/redhat_access_insights
python __init__.py --no-upload --no-tar-file