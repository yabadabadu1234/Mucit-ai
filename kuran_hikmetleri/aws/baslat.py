import os, sys, boto3
bolge = "us-east-1"
ec2 = boto3.client("ec2", region_name=bolge)
im = sorted(ec2.describe_images(Owners=["amazon"], Filters=[{"Name": "name", "Values": ["Deep Learning OSS Nvidia Driver AMI GPU PyTorch*Ubuntu 22.04*"]}, {"Name": "state", "Values": ["available"]}])["Images"], key=lambda x: x["CreationDate"])[-1]
tip = sys.argv[1] if len(sys.argv) > 1 else "g6e.2xlarge"
kok = sys.argv[2] if len(sys.argv) > 2 else "شدد"
kod = open(os.path.join(os.path.dirname(__file__), "onyukleme.sh"), encoding="utf-8").read().replace("${MUCIT_KOK:-شدد}", kok)
r = ec2.run_instances(ImageId=im["ImageId"], InstanceType=tip, MinCount=1, MaxCount=1, UserData=kod,
    IamInstanceProfile={"Name": "mucit-vllm-rolu"}, InstanceInitiatedShutdownBehavior="terminate",
    BlockDeviceMappings=[{"DeviceName": "/dev/sda1", "Ebs": {"VolumeSize": 600, "VolumeType": "gp3", "DeleteOnTermination": True}}],
    InstanceMarketOptions={"MarketType": "spot", "SpotOptions": {"SpotInstanceType": "one-time", "InstanceInterruptionBehavior": "terminate"}},
    TagSpecifications=[{"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": "mucit-vllm-deneme"}]}])
print(r["Instances"][0]["InstanceId"], im["ImageId"], tip)
