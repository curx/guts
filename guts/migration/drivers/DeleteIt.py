from vmware import VMWareDriver

### Remove it later

def print_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = virtual_machine.summary
    print("Name       : ", summary.config.name)
    print("Template   : ", summary.config.template)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("Instance UUID : ", summary.config.instanceUuid)
    print("Bios UUID     : ", summary.config.uuid)
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            print("VMware-tools: ", tools_version)
        else:
            print("Vmware-tools: None")
        if ip_address:
            print("IP         : ", ip_address)
        else:
            print("IP         : None")
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")


obj = VMWareDriver()

#for vm in obj.get_all_vms():
#    print_vm_info(vm)

#print (obj.clone_vm("502ce17f-ab83-b13f-142e-cdc8c4a0a65e"))
print (obj.migrate("502ce17f-ab83-b13f-142e-cdc8c4a0a65e"))
#print (obj.find_vm_by_uuid("502ce17f-ab83-b13f-142e-cdc8c4a0a65e"))

#import pdb; pdb.set_trace()

#obj.list_vm_snapshots("502ce17f-ab83-b13f-142e-cdc8c4a0a65e")
