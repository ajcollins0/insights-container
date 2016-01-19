# !/usr/bin/python
# Copyright (C) 2016 Red Hat, All rights reserved.
# AUTHORS: Alex Collins <alcollin@redhat.com>

import os
import sys
import util
import docker
from mount import DockerMount, Mount, MountError
from emulator import Emulator, EmulatorError


def force_clean(cid, client, emu):
    """ force unmounts and removes any block devices
        to prevent memory corruption """

    driver = client.info()['Driver']

    emu.unmount(force=True)

    # unmount path
    Mount.unmount_path(emu.tmp_image_dir,force=True)

    # if device mapper, do second unmount and remove device
    if driver == 'devicemapper':
        Mount.unmount_path(emu.tmp_image_dir,force=True)
        device = client.inspect_container(cid)['GraphDriver']['Data']['DeviceName'] 
        Mount.remove_thin_device(device,force=True)

def mount_obj(path, obj, driver):
    """ mounts the obj to the given path """

    # docker mount creates a temp image
    # we have to use this temp image id to remove the device 
    path, new_cid = DockerMount(path).mount(obj)
    if driver == 'devicemapper':
        DockerMount.mount_path(os.path.join(path, "rootfs"), path, bind=True)

    return new_cid

def unmount_obj(path, cid, driver):
    """ unmount the given path """

    # If using device mapper, unmount the bind-mount over the directory
    if driver == 'devicemapper':
        Mount.unmount_path(path)

    DockerMount(path).unmount(cid)

def remove_old_data():
    """ deleted old output """

    temp_dir = "/var/tmp/docker/"
    cmd = ['rm', '-rf', temp_dir]
    r = util.subp(cmd)
    if r.return_code != 0:
        raise ValueError(str("Unable to remove directory %s."% temp_dir))

def scan(images=True):
    """ scanning method that will scan all images or containers """

    # FIXME using default 'unix://var/run/docker.sock'
    client = docker.Client(base_url='unix://var/run/docker.sock')
    emu = Emulator()

    objs = client.images(quiet=True) 
    driver = client.info()['Driver']

    # If there are no images/containers on the machine, objs will be ['']
    if objs == ['']:
        return

    # does actual work here!
    for im in objs:
        try:

            emu.create_dirs()
            cid = mount_obj(emu.tmp_image_dir, im, driver)

            if emu.is_applicable():
                print "scanning " + im[:12]
                emu.intial_setup()
                emu.chroot_and_run()
                emu.unmount()
            else:
                print im[:12] + " is not RHEL based"

            unmount_obj(emu.tmp_image_dir, cid, driver)
            emu.remove_dirs()


        except MountError as dme:
            force_clean(cid, client, emu)
            print "Red Hat Insights was unable to complete " \
                  "due to the below error. All mounts and devices " \
                  "have been removed."
            raise ValueError(str(dme))
        except EmulatorError as eme:
            force_clean(cid, client, emu)
            print "Red Hat Insights was unable to complete " \
                  "due to the below error. All mounts and devices " \
                  "have been removed."
            raise ValueError(str(eme))

    emu.gather_data()

def main():

    remove_old_data()
    print "Scanning Images:"
    scan()

if __name__ == '__main__':

    if os.geteuid() != 0:
        raise ValueError("This MUST must be run as root.")
    main()
