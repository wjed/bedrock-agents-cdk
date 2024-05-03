
# Bedrock Agents with AWS CDK

## Prerequisites
* Mac or linux, untested on Windows but you can try in git bash or a miniconda terminal
* Install AWS CDK CLI and follow the get started guide to get the proper permissions enabled in your AWS account
    - https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
* Install miniconda for python https://docs.anaconda.com/free/miniconda/miniconda-install/

## Quick Start

```bash
conda create -n bedrock-agents python=3 -y
conda activate bedrock-agents
pip install -r requirements.txt
cdk bootstrap # This will add the CDK roles to enable CDK to work in the account
cdk deploy # Deploys the bedrock agent infrastructure to your account
```
All the infrastructure is in place! Now, to test it, copy the agent id and alias ID outputted at the end of the `cdk deploy` command. It will look something like 
```txt
Outputs:
CdkStack.AgentAliasId = SIJ6NAPWJB
CdkStack.AgentId = BV8OL8URO7
```

Then run the example script to test it out. You'll need to use your own ID and alias ID values
```bash
python example.py --agent-id BV8OL8URO7 --alias-id SIJ6NAPWJB --query "chicken stir fry"
```

Once you're done, tear down the infrastructure with
```bash
cdk destroy # Remove the resources that were used
```



