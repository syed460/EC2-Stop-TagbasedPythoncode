#!/bin/python3
import boto3, json


def lambda_handler(event, context):

    #define the connection and set the region
    ec2_res = boto3.resource(service_name='ec2', region_name='eu-west-1')
    ec2_cli = boto3.client(service_name='ec2', region_name='eu-west-1')   
    
    
    def publish_sns(instances,RunningInstances):
        client = boto3.client(service_name='sns', region_name='eu-west-1')
        response = ec2_cli.describe_instances(InstanceIds=RunningInstances)['Reservations']
        Running_Instances = []
        for each in response:
            #pprint(each)
            for item in each['Instances']:
                for tag in item['Tags']:
                    if tag['Key'] == 'Name':
                        Running_Instances.append(tag['Value'])
        print("Hostname of the instances: {}".format(Running_Instances))

        count=len(Running_Instances)
        message = ("Hi Team,\n\nPlease find the below list of servers have been STOPPED as per daily power-0ff schedule.\n\nHostname = {a}\nNumber of servers = {b}\n\nRegards,\nTeam".format(a=Running_Instances,b=count))
        sub =("EC2 Instance Daily Power-OFF Schedule")
        sns_arn=("<???>")

        client.publish(TopicArn =sns_arn,Message=message,Subject=sub)
        print ("Notification has been sent to email :)")
    
    def publish_sns_2(instances,RunningInstances):
        client = boto3.client(service_name='sns', region_name='eu-west-1')

        message = ("Hi Team,\n\nThere are no servers to STOP in the env.\n\nPlease login to the AWS console and check it.\n\nRegards,\nTeam")
        sub =("EC2 Instance Daily Power-OFF Schedule")
        sns_arn=("???")

        client.publish(TopicArn =sns_arn,Message=message,Subject=sub)
        print ("message been sent to email :)")
    
    # all running EC2 instances.
    filters = [{'Name': 'tag:shutdown_tag','Values': ['EC2_Stop']},{'Name': 'instance-state-name', 'Values': ['running']}]
    
    #filter the instances which are stopped
    instances = ec2_res.instances.filter(Filters=filters)
    
    #locate all running instances
    RunningInstances = [instance.id for instance in instances]
    
    
    if len(RunningInstances) > 0:
        #perform the shutdown
        shuttingDown = ec2_res.instances.filter(InstanceIds=RunningInstances).stop()
        waiter=ec2_cli.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=RunningInstances)
        print("instance have been stopped :(")
        send_sns = publish_sns(instances,RunningInstances)
    
    else:
        print("nothing to stop")
        send_sns = publish_sns_2(instances,RunningInstances)
