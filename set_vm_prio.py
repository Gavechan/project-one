#!/usr/bin/python
#written by chen ruining 
# to do：
#把不同网卡名字命名那里重构一下，line63 & 67
#
#
import libvirt
import time
import os

from xml.etree import ElementTree
conn = libvirt.open("qemu:///system")
temp=[0 for x in range(0, 10)]
RX_NUMBER_COLUMN=1
TX_NUMBER_COLUMN=0
ROUND_TIME=1
list_of_VM_neededtoBeMonitorred=['macvtap0','macvtap1']

#input is different packets number in different VMs, calculated according priority based on that
def calculate_priority(numlist): 
        base = 1024
        prio_rate = []
        prio = []
        sum = 0.0
        for i in numlist:
                sum+=i
        if sum==0.0:
                sum+=1
        for i in range(len(numlist)):
                prio_rate.append(numlist[i]/sum)
                prio.append(int(base * prio_rate[i]))
        return prio

#get different packets number in different VMs
def printNicInfo(str,midvalue):
    global ifaceinfo
    ifaceinfo = domain.interfaceStats(iface)
    flowOfPackets = int(ifaceinfo[RX_NUMBER_COLUMN]) - midvalue
    #print(flowOfPackets,domain.name(), iface, ifaceinfo)
    return flowOfPackets

#set each VM's priority accrordingly
def set_vm_priority(priolist):
        vm_dom_list=[]
        conn = libvirt.open("qemu:///system")
        for id in conn.listDomainsID():
                domain = conn.lookupByID(id)
                vm_dom_list.append(domain.name())
        for i in range(len(priolist)):
                print 'vm_dom_list name', vm_dom_list[i],'cpu_sahres',priolist[i]
                os.system('virsh schedinfo %s --set cpu_shares=%s '%(vm_dom_list[i],priolist[i]))
        conn.close()

#main loop
list_of_iface=[]
while True:
    time.sleep(ROUND_TIME)
    listOfFlow = []
    for id in conn.listDomainsID():
        domain = conn.lookupByID(id)
        tree = ElementTree.fromstring(domain.XMLDesc())
        ifaces = tree.findall('devices/interface/target')
        for i in ifaces:
            iface = i.get('dev')
            list_of_iface.append(iface)
        for iface in list_of_iface:
            for iface in list_of_VM_neededtoBeMonitorred:
                listOfFlow.append(printNicInfo(iface,temp[len(listOfFlow)]))
                temp[length] = int(ifaceinfo[RX_NUMBER_COLUMN])
    set_vm_priority(calculate_priority(listOfFlow))
    print
conn.close()
