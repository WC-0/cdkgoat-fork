from aws_cdk import core, \
    aws_s3 as s3, \
    aws_ec2 as ec2, \
    aws_kms as kms, \
    aws_iam as iam
    
from aws_cdk.aws_ec2 import Peer, Port
from aws_cdk.core import RemovalPolicy
from aws_cdk.core import CfnOutput
from aws_cdk.core import SecretValue



class CdkGoatStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self,
                      'vpc1'
                      )

        bucket_name = 'my-cdk-goat-bucket'
        s3.Bucket(self,
                  bucket_name,
                  bucket_name=bucket_name,
                  access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                  removal_policy=RemovalPolicy.DESTROY)

        ec2.Volume(self, 'vol1', availability_zone='us-east-1a', size=core.Size.gibibytes(8))

        sg = ec2.SecurityGroup(self,
                               'sg1',
                               vpc=vpc)
        sg.add_ingress_rule(Peer.any_ipv4(), Port.tcp(22))

        kms.Key(self, 'kms1')

        multipart_user_data = ec2.MultipartUserData()
        commands_user_data = ec2.UserData.for_linux()
        multipart_user_data.add_user_data_part(commands_user_data, ec2.MultipartBody.SHELL_SCRIPT, True)

        # Adding commands to the multipartUserData adds them to commandsUserData, and vice-versa.
        multipart_user_data.add_commands("touch /root/multi.txt")
        commands_user_data.add_commands("touch /root/userdata.txt")

        # Creates a new IAM user, access and secret keys
        user = iam.User(self, "Bob")
        cfn_access_key = iam.CfnAccessKey(self, "MyCfnAccessKey",
            user_name=user.user_name,
            serial=2)
        CfnOutput(self, "SecretKey", value=cfn_access_key.attr_secret_access_key)