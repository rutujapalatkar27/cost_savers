# cost_savers
AWS resource management project

## Introduction 
AWS Resources management Script Project 
This project contains custom designed script for listing, stopping and starting EC2 Instances.  

## Prerequisites
1. install aws cli tool

$ curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
$ sudo installer -pkg AWSCLIV2.pkg -target /

2. You will need to have AWS API credentials configured. You can use ~/.aws/crdentials file 

$ vi ~/.aws/credentials

3. Install AWS SDK for python (Boto3)

$ pip install boto3

4. Install python 

$ sudo apt update
$ sudo apt install python3

## Run the script

1. By default it will list all ec2 instances in the region "us-east-1"
$ python3 trial_4.py 

2. Give different region with flag -r 
$ python3 trial_4.py -r <region>

3. Perform different action like list,stop or start using -a, --action flag 
$ python3 trial_4.py -r <region> -a <action>

4. Perform action only on some of the instances by using -i, --include flag
$ python3 trial_4.py -r <region> -a <action> -i <name_of_instances>

5. Perform action on all instances excluding some of them by -e, --exclude flag 
$ python3 trial_4.py -r <region-of-your-choice> -a <action> -e <instances_name_you_want_to_exclude>

6. You can also filter instances depending upon their type by flag -t, --type
$ python3 trial_4.py -r <region> -a <action> -t <type_of_instance>

7. You can also filter instances depending upon their ids by flag -id, --id
$ python3 trial_4.py -r <region> -a <action> -id <instance_id> 

8. You can also perform all the above actions by giving -f, --force option wherein it will not ask for confirmation
$ python3 trial_4.py -r <region> -a <action> -f 
  
9. Choose whether to assume role or not depending upon your access permission by the flag -assume, --assume
  $ python3 trial_4.py -assume -a list
  


