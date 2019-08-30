from auto_class.generate import from_yaml, from_dict_literal_str
from auto_class import intermediate_representation as ir


def test_from_yaml():
    document = """
Type: clone
Basic:
  name: '' # Required
  Source: '' # Required : f:Source Only applies to clone, template, and image types. For clone and template, can be a vm
             # name or a vm UUID. For image, must be a path to an OVA in the vss-ISOs repository, or a path to an
             # image in your vskey-stor
  OS: '' # Required : Guest Operating System name or Id.
  CPU Count: 1 # Optional : CPU count (Default: 1 CPU).
  Memory: 1 # Optional : Memory in GB (Default: 1 GB).
  Folder: '' # Required
  Disks: # Required
    - 40
  ISO: '' # Optional : ISO name or path to mount upon creation.
  Fault Domain: '' # Optional : Domain name or ID to deploy (Default: provided by API).
  High IO: false # Optional : created with a VMware Paravirtual SCSIController.
  Form HA Group: false # Optional : Instruct VM-Deploy to create a VSS HA group of all VMs listed here

Networking:
  Apply Custom Spec: false # Required: Only applies to template and clone types. Attempt to apply a custom spec to this VM. (default: no)
  Hostname: ''
  Domain: '' # (Custom Spec) Required: full search domain
  DNS Servers:  # (Custom Spec) Required (if dhcp:false): Remove if using VSS-PUBLIC or any other DHCP based network
    - ''
  Interfaces:
    - Network Name: '' # Required for image and from-scrath, optional for template and clone: Network name or network ID (default: source vm network)
      DHCP: '' # (Custom Spec) Required: Whether to use DHCP for interface configuration (default: no)
      IP Address: '' # (Custom Spec) Required (if dhcp:false): CIDR format. Remove if using VSS-PUBLIC or any other DHCP based network
      Gateway Address: '' # (Custom Spec) Required (if dhcp:false): Remove if using VSS-PUBLIC or any other DHCP based network

Metadata:
  Description: '' # Optional : Description of virtual machine
  Usage: '' # Optional : Usage between Prod | Dev | QA | Test (Default for template / clone: source template / vm. Default for image / from-scratch: Test)
  Billing: '' # Optional for Clone / Template, Required for image / from-scratch: Billing department
  Inform:  # Optional for Clone / Template, Required for image / from-scratch: list of email addresses.
    - ''
  Admin: # Optional : Defaults to the person submitting this request
    Name: ''
    Email Address: ''
    Phone Number: ''
  Notes:  # Optional key:value metadata to attach to the VM. Only visible to the API and VMWare client, not to the VM itself
    ExampleNote: Value
  Guest Info: # Optional key:value metadata to attach to the VM. Only visible to the API and the VM Guest OS (through vmware tools), not visible in VMWare Client. Note: VSS API calls this 'extra_config'
    ExampleKey: Value
  VSS Service: '' # Optional : Name of the VSS service this VM provides or supports. Run `vss-cli service ls -a` for a list of services
  VSS Options:
    Reset On Restore: false # Optional : Undocumented
    Reboot On Restore: false # Optional : Undocumented
"""
    name = 'ParentClass'
    append = """
def test_method(self):
    pass
"""
    result = from_yaml(document, name, append_code=append)
    assert isinstance(result, str)


def test_from_dict_literal_str():
    dict_str = '''<class 'dict'>: {'folders': {'group-v15160': {'children': [], 'name': 'UAT', 'parent': 'SHARED2', 'path': 'EIS Systems Group > Internal > EASI > SHARED2 > UAT'}, 'group-v5669': {'children': [], 'name': 'Arbor Pte', 'parent': 'DUA', 'path': 'EIS Systems Group > External > DUA > Arbor Pte'}, 'group-v4609': {'children': [{'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v599'}, 'name': 'WTS'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v508'}, 'name': 'ICS'}], 'name': 'Video', 'parent': 'ACT', 'path': 'ITS > ACT > Video'}, 'group-v5718': {'children': [], 'name': 'Security', 'parent': 'DUA', 'path': 'EIS Systems Group > External > DUA > Security'}, 'group-v1282': {'children': [], 'name': 'Mail Routing', 'parent': 'Network Services', 'path': 'ITS > Network Services > Mail Routing'}, 'group-v312': {'children': [{'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v10391'}, 'name': 'TRN'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v10390'}, 'name': 'UAT'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v9388'}, 'name': 'SIT'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v9025'}, 'name': 'SB'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v498'}, 'name': 'QA'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v497'}, 'name': 'PRD'}, {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/folder/group-v496'}, 'name': 'DEV'}], 'name': 'NGSIS', 'parent': 'Internal', 'path': 'EIS Systems Group > Internal > NGSIS'}, 'group-v14536': {'children': [], 'name': 'ACT LAMP1', 'parent': 'ACT', 'path': 'ITS > ACT > ACT LAMP1'}, 'group-v367': {'children': [], 'name': 'Campus+Facility Planning', 'parent': 'External', 'path': 'EIS Systems Group > External > Campus+Facility Planning'}}, 'networks': {'dvportgroup-11035': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11035'}, 'accessible': True, 'admin': 'Joe Bate:647-534-9591:joe.bate@utoronto.ca', 'client': 'ISEA', 'description': 'Exchange 2016 Application Tier', 'label': 'VL-1797-EXCH-APP 128.100.197.128/26 Exchange 2016 Application Tier', 'moref': 'dvportgroup-11035', 'name': 'VL-1797-EXCH-APP', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11035/perm'}, 'ports': 32, 'subnet': '128.100.197.128/26'}, 'dvportgroup-11068': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11068'}, 'accessible': True, 'admin': 'Ted  Sikorski:416-978-6602:ted.sikorski@utoronto.ca', 'client': 'EIS', 'description': 'EIS managed network for EASI Prod environments', 'label': 'VL-0313-ADMIN-PROD 142.150.183.0/25 EIS managed network for EASI Prod environments', 'moref': 'dvportgroup-11068', 'name': 'VL-0313-ADMIN-PROD', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11068/perm'}, 'ports': 65, 'subnet': '142.150.183.0/25'}, 'dvportgroup-11017': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11017'}, 'accessible': True, 'admin': 'Joe Bate:647-534-9596:joe.bate@utoronto.ca', 'client': 'ISEA', 'description': 'QA Exchange 2016 Data Tier', 'label': 'VL-1974-EXCHQA-DATA 128.100.115.192/26 QA Exchange 2016 Data Tier', 'moref': 'dvportgroup-11017', 'name': 'VL-1974-EXCHQA-DATA', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11017/perm'}, 'ports': 32, 'subnet': '128.100.115.192/26'}, 'dvportgroup-11025': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11025'}, 'accessible': True, 'admin': 'John Calvin:416-978-6878:john.calvin@utoronto.ca', 'client': 'EIS', 'description': 'KualiReady business continuity systems', 'label': 'VL-1159-KUALIREADY 128.100.159.0/24 KualiReady business continuity systems', 'moref': 'dvportgroup-11025', 'name': 'VL-1159-KUALIREADY', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11025/perm'}, 'ports': 32, 'subnet': '128.100.159.0/24'}, 'dvportgroup-10991': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10991'}, 'accessible': True, 'admin': 'Joe Bate:647-534-9591:joe.bate@utoronto.ca', 'client': 'ISEA', 'description': 'NGSIS Tier1 User Acceptance Testing Mgmt', 'label': 'VL-1979-NGSIS-TIER1-UAT-MGMT 10.192.203.0/24 NGSIS Tier1 User Acceptance Testing Mgmt', 'moref': 'dvportgroup-10991', 'name': 'VL-1979-NGSIS-TIER1-UAT-MGMT', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10991/perm'}, 'ports': 32, 'subnet': '10.192.203.0/24'}, 'dvportgroup-10762': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10762'}, 'accessible': True, 'admin': 'USG:416-978-6946:usg@utcc.utoronto.ca', 'client': 'EIS', 'description': 'Computer & Network Services, departmental ethernet 1', 'label': 'VL-1102-UTCS 128.100.102.0/24 Computer & Network Services, departmental ethernet 1', 'moref': 'dvportgroup-10762', 'name': 'VL-1102-UTCS', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10762/perm'}, 'ports': 128, 'subnet': '128.100.102.0/24'}, 'dvportgroup-10992': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10992'}, 'accessible': True, 'admin': 'Joe Bate:647-534-9591:joe.bate@utoronto.ca', 'client': 'ISEA', 'description': 'Business Intelligence Tier1 Mgmt', 'label': 'VL-2262-BI-TIER1-MGMT 10.192.203.128/25 Business Intelligence Tier1 Mgmt', 'moref': 'dvportgroup-10992', 'name': 'VL-2262-BI-TIER1-MGMT', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10992/perm'}, 'ports': 32, 'subnet': '10.192.203.128/25'}, 'dvportgroup-10989': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10989'}, 'accessible': True, 'admin': 'Joe Bate:647-534-9591:joe.bate@utoronto.ca', 'client': 'ISEA', 'description': 'NGSIS Tier1 User Acceptance Testing', 'label': 'VL-1978-NGSIS-TIER1-UAT 10.192.202.0/24 NGSIS Tier1 User Acceptance Testing', 'moref': 'dvportgroup-10989', 'name': 'VL-1978-NGSIS-TIER1-UAT', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-10989/perm'}, 'ports': 32, 'subnet': '10.192.202.0/24'}, 'dvportgroup-11032': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11032'}, 'accessible': True, 'admin': 'Windows Institutional Server Support:416-946-4009:eis.wss@utoronto.ca', 'client': 'EIS', 'description': 'Pandora', 'label': 'VL-1189-PANDORA 128.100.189.0/24 Pandora', 'moref': 'dvportgroup-11032', 'name': 'VL-1189-PANDORA', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11032/perm'}, 'ports': 32, 'subnet': '128.100.189.0/24'}, 'dvportgroup-11273': {'_links': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11273'}, 'accessible': True, 'admin': 'Joe Bate:647-534-9591:joe.bate@utoronto.ca', 'client': 'ISEA', 'description': 'NGSIS Tier1 Production', 'label': 'VL-2256-NGSIS-TIER1-PR 10.192.213.0/25 NGSIS Tier1 Production', 'moref': 'dvportgroup-11273', 'name': 'VL-2256-NGSIS-TIER1-PR', 'permission': {'self': 'https://cloud-api.eis.utoronto.ca/v2/network/dvportgroup-11273/perm'}, 'ports': 32, 'subnet': '10.192.213.0/25'}}, 'sib_codes': {'type': {'00': 'Mystery VM', '01': 'Standard billing', '02': 'Centrally Funded VM. These are VM that were early adopters and are grandfathered as free. Any big expansion in resources may disqualify the VM from this privileged status. This does not include support costs.', '03': 'Internal ITS system - None Billable', '04': 'Non-ITS Systems Free', '05': 'StarRez Servers. Patrick negotiated a deal with EASI/Housing services where the suite of servers would cost them $27,600 annually.', '06': 'Orbis. Standard rates are split 5 ways with Rotman and Engineering splitting 1/3 of the cost and UTM, UTSC and St. George Career Centers splitting the remaining 2/3.', '07': 'Faculty of Medicine - Entrada system suite. The entire suite of VMs (10 VMs as at 2017-11-17) and their support will be $20,000 annually.', '08': 'DUA - Negotiated and invoiced by Patrick', '09': 'HPME:\nAnnual server management per server:\xa0 $2,500 \xa0(discounted to $2,000)\nVirtual Machine, estimated cost based on current physical server:\xa0 $1,050 (fee waived for first 2 years, then 50% discount in subsequent years:\xa0 $525 per year)\nTOTAL year 1 (2018-19):\xa0 $2,000\nTOTAL year 2 (2019-20):\xa0 $2,000\nTOTAL year 3 & onward:\xa0 $2,525\xa0 Note: cost may rise if the size of the VM grows substantially, but 50% discount will still apply to any additional resources added.', '10': 'Retired, powered off VM.', '11': 'Standard billing starting in fiscal year 2019/2020', '12': 'Discount for Arts & Science depts. that are under the support umbrella of Sotira’s IITS group.\n60%\xa0discount\xa0on current list price for vRAM and vCPU (not storage).\n50%\xa0discount\xa0on current UTORrecover pricing.\nThis does not include and discounts for support. Please refer to "IITS Supported Depts" below for a listing of eligible depts.'}, 'client': {'00': 'Uncoded or powered off', '01': 'ITS - EIS:\xa0 Enterprise Infrastructure Solutions', '02': 'ITS - EASI: Enterprise Applications & Solutions Integration', '03': 'ITS - ISEA: Information Security & Enterprise Architecture', '04': 'ITS - ACT: Academic & Collaborative Technologies', '05': 'ITS - PGAC: Planning, Governance & Assessment', '06': 'ACE - Academic and Campus Events', '07': 'BioChemistry', '08': 'Enrollment Services', '09': 'University Affairs', '10': 'Division of Comparative Medicine - ASP host', '11': 'Operations & Finance\xa0(Office of Gov Council)', '12': 'Division of the VP & Provost (Explorance Blue)', '13': 'Division of Comparative Medicine - Sensus', '14': 'Joint Centre for Bioethics', '15': 'Department of Medicine', '16': 'Medical Imaging', '17': 'Applied Science and Engineering - LAMP', '18': 'Environment Health and Safety', '19': 'Research Services - SIG', '20': 'Facilities and Services - Dolphin/Kofax', '21': 'Rotman Commerce', '22': 'VP International & GICR', '23': 'School of Continuing Studies', '24': 'iSchool', '25': 'Health & Well Being', '26': 'Planning and Budget', '27': 'Real Estate Services & Capital Projects - Eclipse', '28': 'Parking Services', '29': 'Internationally Trained Lawyers Program', '30': 'Food Services', '31': 'Facilities Planning', '32': 'The Entrepreneurship Hatchery - APSC', '33': 'Faculty of Nursing', '34': 'Research Services', '35': 'Institute of Medical Science', '36': 'Lockshop', '37': 'Licensed Software Office', '38': 'Pharmacy - dppcms', '39': 'Faculty of Medicine', '40': 'Procurement Services', '41': 'Strategic Communications\nDigital Creative Services 1, in The Office of the VP Communications\nMedia Bank (1306P-SCmedia-prod)', '42': 'Ancillary Services', '43': 'Human Resources and Equity', '44': 'ITS - ACT:\xa0 UofT Homepage', '45': 'Applied Science and Engineering - Bahen', '46': 'Pharmacy - pharmcms', '47': 'Office of the Governing Council', '48': 'Institute of Health Policy, Management and Evaluation', '49': 'Medicine, Finance & Administration', '50': 'CanSSOC (Canadian Shared Security Operations Centre)', '51': 'Strategic Communications\nDigital Creative Services 2, in The Office of the VP Communications\nMedia Relations Blue Book (1609P-mediawp)'}}, 'vms': {'5012a11f-3623-1cd5-544d-ec7d6a502b12': {'is_template': False, 'folder': 'EIS Systems Group > Internal > DataPower', 'hostname': 'dp-syslog', 'ip_addresses': ['128.100.166.115', '192.168.122.1', '172.17.0.1'], 'networks': [{'id': 'dvportgroup-11028', 'name': 'VL-1166-EIS-EASI-PROD2', 'subnet': '128.100.166.0/24'}], 'vss_name': '1508P-datapower-syslog', 'client': 'Uncoded or powered off', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOn', 'description': 'Syslog . backup. Syslog for Acron Data Power. - HIGSR 1959'}, '50127cba-d5bb-ce0d-ca49-360a01fface5': {'is_template': False, 'folder': 'EIS Systems Group > Internal > ROSI > PROD', 'hostname': 'rosi-brkr-prod2', 'ip_addresses': [], 'networks': [{'id': 'dvportgroup-11068', 'name': 'VL-0313-ADMIN-PROD', 'subnet': '142.150.183.0/25'}, {'id': 'dvportgroup-11059', 'name': 'VL-2150-VSVC-ADMIN', 'subnet': '142.150.150.0/24'}], 'vss_name': '1307P-rosi-brkr-prod2', 'client': 'Uncoded or powered off', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOff', 'description': None}, '501205e3-a254-9be2-a7ba-c0de1c0005fc': {'is_template': False, 'folder': 'ITS > ACT > Quercus Apps PRD', 'hostname': 'gm-mariadb-1', 'ip_addresses': ['142.1.176.154'], 'networks': [{'id': 'dvportgroup-11051', 'name': 'VL-1260-EIS-WWW', 'subnet': '142.1.176.0/24'}], 'vss_name': '1806P-gm-mariadb-1', 'client': 'ITS - ACT: Academic & Collaborative Technologies', 'client_type': 'Standard billing', 'fault_domain': 'FD1', 'power': 'poweredOn', 'description': 'Group manager mariadb-1'}, '520429a3-b0a1-d3bb-8f5a-42b1a73abed6': {'is_template': False, 'folder': 'EIS Systems Group > Internal > NGSIS > DEV', 'hostname': 'scm.kuali.utoronto.ca', 'ip_addresses': [], 'networks': [{'id': 'dvportgroup-11066', 'name': 'VL-0309-ADMIN-DEV', 'subnet': '142.150.182.0/25'}], 'vss_name': '1204D-kuali4', 'client': 'Uncoded or powered off', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOff', 'description': None}, '5012b2e0-843b-7702-4c65-f8fa66240eb6': {'is_template': False, 'folder': 'ITS > Network Services > smtpauth', 'hostname': 'bureau92', 'ip_addresses': ['128.100.132.250'], 'networks': [{'id': 'dvportgroup-11021', 'name': 'VL-1132-MITTERE', 'subnet': '128.100.132.0/24'}], 'vss_name': '1304P-bureau92', 'client': 'Uncoded or powered off', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOn', 'description': None}, '5012385f-a2b3-10c1-00b0-6c7b22cc896c': {'is_template': False, 'folder': 'ITS > Enterprise ADS > 365Proj', 'hostname': 'utsgqa-e13-1.adqa.utoronto.ca', 'ip_addresses': ['128.100.115.196'], 'networks': [{'id': 'dvportgroup-11017', 'name': 'VL-1974-EXCHQA-DATA', 'subnet': '128.100.115.192/26'}], 'vss_name': '1703Q-utsgqa-e13-1', 'client': 'Uncoded or powered off', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOn', 'description': 'Template. Template. Template, updating software. - HIGR 1264'}, '50120f72-41be-40ea-8e11-97744008d2ce': {'is_template': False, 'folder': 'EIS Systems Group > Internal > ROSI > PROD', 'hostname': 'lbrt-rxp-prd2', 'ip_addresses': ['128.100.166.176'], 'networks': [{'id': 'dvportgroup-11028', 'name': 'VL-1166-EIS-EASI-PROD2', 'subnet': '128.100.166.0/24'}], 'vss_name': '1806P-lbrt-rxp-prd2', 'client': 'ITS - EASI: Enterprise Applications & Solutions Integration', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOn', 'description': 'ROSI Express Prod Server 1'}, '50126fa4-5c3d-e813-30d8-09df98d54991': {'is_template': False, 'folder': 'EIS Systems Group > Internal > ACORN', 'hostname': 'jm-test-04', 'ip_addresses': ['128.100.100.205'], 'networks': [{'id': 'dvportgroup-11012', 'name': 'VL-1100-MRF', 'subnet': '128.100.100.0/24'}], 'vss_name': '1903T-jm-test-04', 'client': 'Unknown', 'client_type': 'Unknown', 'fault_domain': 'FD4', 'power': 'poweredOn', 'description': 'EASI jMeter server 4 for Performance Testing'}, '5012c656-acbe-a1ae-7f57-78246baf50ba': {'is_template': False, 'folder': 'EIS Systems Group > Internal > NGSIS > PRD', 'hostname': 'ngsis-prod-cc-3.easi.utoronto.ca', 'ip_addresses': ['10.192.213.27', '10.192.214.27'], 'networks': [{'id': 'dvportgroup-11273', 'name': 'VL-2256-NGSIS-TIER1-PR', 'subnet': '10.192.213.0/25'}, {'id': 'dvportgroup-11274', 'name': 'VL-2257-NGSIS-TIER1-PR-MGMT', 'subnet': '10.192.214.0/25'}], 'vss_name': '1711P-ngsis-prod-cc-3', 'client': 'ITS - EASI: Enterprise Applications & Solutions Integration', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD2', 'power': 'poweredOn', 'description': 'IBM WebSphere Liberty Collective Server for GEMS NGSIS PROD\n environment'}, '5012c766-91a3-4c12-e701-483e7a0fdbda': {'is_template': False, 'folder': 'ITS > Network Services > edge', 'hostname': None, 'ip_addresses': [], 'networks': [{'id': 'dvportgroup-11021', 'name': 'VL-1132-MITTERE', 'subnet': '128.100.132.0/24'}], 'vss_name': '1311T-clone-test', 'client': 'Uncoded or powered off', 'client_type': 'Internal ITS system - None Billable', 'fault_domain': 'FD1', 'power': 'poweredOn', 'description': None}}}'''
    result = from_dict_literal_str(dict_str, 'Data')
    assert result == """

from dataclasses import field
from typing import List, Dict, Any, Type, ClassVar

from marshmallow import Schema
from marshmallow.fields import Field
from marshmallow_dataclass import dataclass

@dataclass
class Folders:
    children: List[Any] 
    name: str 
    parent: str 
    path: str 
    
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class Networks:
    _links: Dict[str,str] 
    accessible: bool 
    admin: str 
    client: str 
    description: str 
    label: str 
    moref: str 
    name: str 
    permission: Dict[str,str] 
    ports: int 
    subnet: str 
    
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class Sib_codes:
    type: Dict[str,str] 
    client: Dict[str,str] 
    
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class Networks1:
    id: str 
    name: str 
    subnet: str 
    
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class Vms:
    is_template: bool 
    folder: str 
    hostname: str 
    ip_addresses: List[str] 
    networks: List[Networks1] 
    vss_name: str 
    client: str 
    client_type: str 
    fault_domain: str 
    power: str 
    description: str 
    
    Schema: ClassVar[Type[Schema]] = Schema

@dataclass
class Data:
    folders: Dict[str,Folders] 
    networks: Dict[str,Networks] 
    sib_codes: Sib_codes 
    vms: Dict[str,Vms] 
    
    Schema: ClassVar[Type[Schema]] = Schema

"""


if __name__ == '__main__':
    test_from_dict_literal_str()
