#!/usr/bin/python
#last edited by crn

import libvirt
import time
import os

from xml.etree import ElementTree
conn = libvirt.open("qemu:///system")
interfaces_list=['macvtap0','macvtap1']
temp=[0 for x in range(0, 10)]
#0-6 represent rx_bytes, rx_packet,rx_errs,rx_drop,tx_bytes,tx_packets,tx_err,tx_drops

RX_NUMBER_COLUMN=1
TX_NUMBER_COLUMN=0
ROUND_TIME=1
#magic num used to contrl first print act
magic_num=0
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
def get_nic_info(str,last_time_value):
    global ifaceinfo
    ifaceinfo = domain.interfaceStats(iface)
    flowOfPackets = int(ifaceinfo[RX_NUMBER_COLUMN]) - last_time_value
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

#only trace the NIC interface we are intersted
def filter_nic_info(iface):
        if iface in interfaces_list:
                length=len(list_of_rx_pack)
                list_of_rx_pack.append(get_nic_info(iface,temp[length]))
                temp[length] = int(ifaceinfo[RX_NUMBER_COLUMN])
                #print 'get', list_of_rx_pack
        else:
                return
#main loop
while True:
    time.sleep(ROUND_TIME)
    #list_of_rx_pack represents the num of diffrent flows
    list_of_rx_pack = []
    for id in conn.listDomainsID():
        domain = conn.lookupByID(id)
        tree = ElementTree.fromstring(domain.XMLDesc())
        ifaces = tree.findall('devices/interface/target')
        for i in ifaces:
            iface = i.get('dev')
            filter_nic_info(iface)
    if magic_num != 0:
        set_vm_priority(calculate_priority(list_of_rx_pack))
    magic_num=1
    print
conn.close()
