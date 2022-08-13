import boto3
import botocore
import argparse
from prettytable import PrettyTable
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser()

# Add arguments to the parser
parser.add_argument('-i', '--include', 
                    type=str,  
                    nargs='+',
                    help='value for tag:name')
parser.add_argument('-r', '--region', 
                    default="us-east-1", 
                    help='enter region')
parser.add_argument('-e', '--exclude', 
                    type=str,  
                    nargs='+',
                    help='value for exclude tag:name')
parser.add_argument('-t', '--type', 
                    type=str,  
                    nargs='+',
                    help='value for type of instance')
parser.add_argument('-f', '--force',
                    action= 'store_true',
                    help='force stop instances')
parser.add_argument('-a', '--action',
                    default="list",
                    type=str,
                    choices=['list', 'start', 'stop'],
                    help='perform given action on instances')
parser.add_argument('-id', '--id',
                    type=str,
                    nargs='+',
                    help='enter instance id')
args = parser.parse_args()
try:
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(RoleArn =  "arn:aws:iam::729111267627:role/webfocus-eks",
                                        RoleSessionName = "AssumeRoleSession1",
                                        DurationSeconds = 1800)
    session = boto3.Session(
        aws_access_key_id     = assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key = assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token     = assumed_role['Credentials']['SessionToken'],
        region_name           = args.region
    )
    ec2 = session.client("ec2", region_name= args.region)
except ClientError as e:
    if e.response['Error']['Code'] == 'ExpiredToken':
        print("The security token included in the request is expired")
        exit()
    else:
        print("Unexpected error: %s" % e)

#filters 
ec2_running={'Name': 'instance-state-name', 'Values': ['running']}                                           
ec2_include_tag={"Name":"tag:Name", "Values": args.include}
ec2_type = {'Name':'instance-type','Values': args.type}
ec2_stopped={'Name': 'instance-state-name', 'Values': ['stopped']} 
ec2_instance_id= {'Name': 'instance-id', 'Values': args.id} 

#table
x=PrettyTable(print_empty=False)
x.field_names=["Name", "Region", "Id", "Type","Status", "Owner"]

#display function
def display(reservations):
    for reservation in reservations["Reservations"]:
        for instance in reservation["Instances"]:
            name=instance['InstanceId']
            for x4 in instance['Tags']:
                if x4['Key']=='Name':
                    name=x4['Value']
                    owner=name.split('-')[0]
            x.add_row([name, args.region, instance['InstanceId'], instance['InstanceType'], instance['State']['Name'],owner])
    print(x)

#collecting all regions in a list
ec2_regions=boto3.resource("ec2")
regions=[]
for region in ec2_regions.meta.client.describe_regions()['Regions']:
    regions.append(region['RegionName'])
#checking if region is valid 
if args.region not in regions:
    print("Enter valid region and try again")
    exit()

#exclude function
def exclude (reservations):
    for j in args.exclude:
        for index,reservation in enumerate(reservations["Reservations"]):
            for instance in reservation["Instances"]:
                for x4 in instance['Tags']:
                    if x4['Key']=='Name':
                        if x4['Value']==j:
                            reservations["Reservations"].pop(index)

#checking the conditions and given action value
if args.include and args.action=="stop":                                        
    reservations = ec2.describe_instances(Filters=[ec2_running,ec2_include_tag])
    display(reservations)
 
elif args.exclude and args.action=="stop":
    reservations = ec2.describe_instances(Filters=[ec2_running])
    exclude(reservations)
    display(reservations)

elif args.type and args.action=="stop":
    reservations = ec2.describe_instances(Filters=[ec2_running,ec2_type])
    display(reservations)

elif args.include and args.action=="start":
    reservations = ec2.describe_instances(Filters=[ec2_stopped,ec2_include_tag])
    display(reservations)

elif args.exclude and args.action=="start":
    reservations = ec2.describe_instances(Filters=[ec2_stopped])
    exclude(reservations)
    display(reservations)

elif args.type and args.action=="start":
    reservations = ec2.describe_instances(Filters=[ec2_stopped,ec2_type])
    display(reservations)

elif args.action=="list" and args.include:
    reservations = ec2.describe_instances(Filters=[ec2_include_tag])
    display(reservations)

elif args.exclude and args.action=="list":
    reservations = ec2.describe_instances()
    exclude(reservations)
    display(reservations)

elif args.type and args.action=="list":
    reservations = ec2.describe_instances(Filters=[ec2_type])
    display(reservations)

elif args.id and args.action=="stop":                                        
    reservations = ec2.describe_instances(Filters=[ec2_running,ec2_instance_id])
    display(reservations)
 
elif args.id and args.action=="start":
    reservations = ec2.describe_instances(Filters=[ec2_stopped,ec2_instance_id])
    display(reservations)

elif args.id:
    reservations = ec2.describe_instances(Filters=[ec2_instance_id])
    display(reservations)

elif args.action=="stop":
    reservations = ec2.describe_instances(Filters=[ec2_running])
    display(reservations)

elif args.action=="start":
    reservations = ec2.describe_instances(Filters=[ec2_stopped])
    display(reservations)

elif args.action=="list":
    reservations = ec2.describe_instances()
    display(reservations)

def stop_instance(reservations):
    client=boto3.client('ec2')
    instance_ids=[]
    for reservation in reservations["Reservations"]:
        for instance in reservation["Instances"]:
            ID=instance['InstanceId']
            instance_ids.append(ID)
            ec2.stop_instances(InstanceIds=[ID]) 
            print("Stopping Instance... "+ str(ID))
            waiter = client.get_waiter('instance_stopped') 
            waiter.wait(InstanceIds=[ID])                                                                                            
            print("Successfully stopped instance: "+ str(ID))
    return instance_ids

def start_instance(reservations):
    client=boto3.client('ec2')
    instance_ids=[]
    for reservation in reservations["Reservations"]:
        for instance in reservation["Instances"]:
            ID=instance['InstanceId']
            instance_ids.append(ID)
            ec2.start_instances(InstanceIds=[ID]) 
            print("Starting Instance... "+ str(ID))
            waiter = client.get_waiter('instance_running') 
            waiter.wait(InstanceIds=[ID])                                                                                            
            print("Successfully started instance: "+ str(ID))
    return instance_ids

if x.rows:
    if args.force and args.action=="stop":
        list=stop_instance(reservations)
        EC2_CLIENT = boto3.client('ec2', region_name=args.region)
        response = EC2_CLIENT.describe_instances(InstanceIds=list)
        print("Following are the stopped instance(s)")
        x.clear_rows()
        display(response)  
    elif args.force and args.action=="start":
        list=start_instance(reservations)
        EC2_CLIENT = boto3.client('ec2', region_name=args.region)
        response = EC2_CLIENT.describe_instances(InstanceIds=list)
        print("Following are the running instance(s)")
        x.clear_rows()
        display(response)
    elif args.action=="stop":
        if input("Do you want to stop above instances? [y/n]") !="y":
            exit
        else:
            list=stop_instance(reservations)
            EC2_CLIENT = boto3.client('ec2', region_name=args.region)
            response = EC2_CLIENT.describe_instances(InstanceIds=list)
            print("Following are the stopped instance(s)")
            x.clear_rows()
            display(response)
    elif args.action=="start":
        if input("Do you want to start above instance(s)? [y/n]") !="y":
            exit
        else:
            list=start_instance(reservations)
            EC2_CLIENT = boto3.client('ec2', region_name=args.region)
            response = EC2_CLIENT.describe_instances(InstanceIds=list)
            print("Following are the running instance(s)")
            x.clear_rows()
            display(response)
else:
    print('There are no matching instance(s) to perform '+ args.action + ' action')

