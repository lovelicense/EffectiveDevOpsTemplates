"""Generating CloudFormation template."""
ApplicationName = "helloworld"
ApplicationPort = "3000"
GithubAccount = "lovelicense"
GithubAnsibleURL = "https://github.com/{}/ansible".format(GithubAccount)

AnsiblePullCmd = "/usr/local/bin/ansible-pull -U {} {}.yml -i localhost".format(GithubAnsibleURL,ApplicationName)

from troposphere import (
            Base64,
                ec2,
                    GetAtt,
                        Join,
                            Output,
                                Parameter,
                                    Ref,
                                        Template,
                                        )

ApplicationPort = "3000"

t = Template()

t.set_description("Effective DevOps in AWS: HelloWorld web application")

t.add_parameter(Parameter(
        "KeyPair",
            Description="Name of an existing EC2 KeyPair to SSH",
                Type="AWS::EC2::KeyPair::KeyName",
                    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
                    ))

t.add_resource(ec2.SecurityGroup(
        "SecurityGroup",
            GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
                SecurityGroupIngress=[
                            ec2.SecurityGroupRule(
                                            IpProtocol="tcp",
                                                        FromPort="22",
                                                                    ToPort="22",
                                                                                CidrIp="218.48.76.232/32",
                                                                                        ),
                                    ec2.SecurityGroupRule(
                                                    IpProtocol="tcp",
                                                                FromPort=ApplicationPort,
                                                                            ToPort=ApplicationPort,
                                                                                        CidrIp="0.0.0.0/0",
                                                                                                ),
                                        ],
                ))

ud = Base64(Join('\n', [
        "#!/bin/bash",
        "yum remove java-1.7.0-openjdk -y",
        "yum install java-1.8.0-openjdk -y",
        "yum install --enablerepo=epel -y git",
        "pip install ansible",
        AnsiblePullCmd,
        "echo '*/10 * * * * root {}' > /etc/cron.d/ansible-pull".format(AnsiblePullCmd)]))

t.add_resource(ec2.Instance(
        "instance",
            ImageId="ami-06cd52961ce9f0d85",
                InstanceType="t2.micro",
                    SecurityGroups=[Ref("SecurityGroup")],
                        KeyName=Ref("KeyPair"),
                            UserData=ud,
                            ))

t.add_output(Output(
        "InstancePublicIp",
            Description="Public IP of our instance.",
                Value=GetAtt("instance", "PublicIp"),
                ))

t.add_output(Output(
        "WebUrl",
            Description="Application endpoint",
                Value=Join("", [
                            "http://", GetAtt("instance", "PublicDnsName"),
                                    ":", ApplicationPort
                                        ]),
                ))

print(t.to_json())
