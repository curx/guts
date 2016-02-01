# Copyright (c) 2015 Aptira Pty Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


"""VMWare Driver"""

import atexit
import requests
import time

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


def wait_for_task(task):
    """ Wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            raise Exception

def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    return obj


class VMWareDriver(object):
    def __init__(self):
        self.con = self.initialize()

    def initialize(self, host="192.168.125.35", port=443,
                   user="administrator@vsphere.local", password="POIpoi99("):
        try:
            self.con = connect.SmartConnect(host=host,
                                            user=user,
                                            pwd=password,
                                            port=port)
            atexit.register(connect.Disconnect, self.con)
        except vmodl.MethodFault as error:
            raise

        self.content = self.con.RetrieveContent()

    def get_all_vms(self):
        try:
            container = self.content.rootFolder # starting point to look into
            view_type = [vim.VirtualMachine]  # object types to look for
            recursive = True  # whether we should look into it recursively

            containerView = self.content.viewManager.CreateContainerView(
                container, view_type, recursive)

            vms = containerView.view
        except vmodl.MethodFault as error:
            raise

        return vms

    def _find_vm_by_name(self, vm_name):
        vms = self.get_all_vms()

        for vm in vms:
            if vm.summary.config.name == vm_name:
                return vm

        raise Exception

    def _find_vm_by_uuid(self, vm_uuid):
        search_index = self.content.searchIndex
        vm = search_index.FindByUuid(None, vm_uuid, True, True)
        if not vm:
            raise Exception

        return vm

    def _find_vm_by_name(self, vm_name):
        vms = self.get_all_vms()

        for vm in vms:
            if vm.summary.config.name == vm_name:
                return vm

        raise Exception

    def _clone_vm(self, vm):
        datacenter_name = None
        vm_folder = None
        datastore_name = None
        cluster_name = None
        resource_pool = None
        power_on = True
        vm_name = "Temp_%s" % (vm.summary.config.name)

        # if none git the first one
        datacenter = get_obj(self.content, [vim.Datacenter], datacenter_name)

        if vm_folder:
            destfolder = get_obj(self.content, [vim.Folder], vm_folder)
        else:
            destfolder = datacenter.vmFolder

        if datastore_name:
            datastore = get_obj(self.content, [vim.Datastore], datastore_name)
        else:
            datastore = get_obj(
                self.content, [vim.Datastore], vm.datastore[0].info.name)

        # if None, get the first one
        cluster = get_obj(self.content, [vim.ClusterComputeResource], cluster_name)

        if resource_pool:
            resource_pool = get_obj(self.content, [vim.ResourcePool], resource_pool)
        else:
            resource_pool = cluster.resourcePool

        # Set relospec
        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.pool = resource_pool

        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = power_on

        task = vm.Clone(folder=destfolder, name=vm_name, spec=clonespec)
        wait_for_task(task)

        return vm_name

    def _export_vm(self, vm, target_path):
        lease = vm.ExportVm()

        try:
            url = lease.info.deviceUrl[0].url
        except IndexError:
            time.sleep(2)
            url = lease.info.deviceUrl[0].url

        r = requests.get(url, verify=False)
        f = open(target_path, 'wb')

        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
        f.close()
        lease.HttpNfcLeaseComplete()

    def _execute_in_vm(self, vm, vm_user='guts', vm_pwd='123', path_to_program="/tmp/myscript.sh", program_arguments=""):
        creds = vim.vm.guest.NamePasswordAuthentication(
                   username=vm_user, password=vm_pwd)
        try:
            pm = self.content.guestOperationsManager.processManager

            ps = vim.vm.guest.ProcessManager.ProgramSpec(
                programPath=path_to_program,
                arguments=program_arguments)
            res = pm.StartProgramInGuest(vm, creds, ps)

            if res > 0:
                print "Program executed, PID is %d" % res

        except IOError, e:
            print e

    def _uninstall_virtio_tools(self, vm):
        self._execute_in_vm(vm)


    def migrate(self, vm_uuid):
        vm = self._find_vm_by_uuid(vm_uuid)

        import pdb; pdb.set_trace()

        # Task - 1: Clone VMWare VM
        #cloned_vm_name = self._clone_vm(vm)
        cloned_vm_name = "Temp_MinimalUbuntu"
        cloned_vm = self._find_vm_by_name(cloned_vm_name)

        # Task - 2: Export VMWare VM
        self._export_vm(cloned_vm, "/root/Images/4/Hello.VMDK")

        # Task - 2: Uninstall VirtIO Tools
        #self._uninstall_virtio_tools(cloned_vm)
