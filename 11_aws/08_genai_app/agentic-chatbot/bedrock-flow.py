import boto3
import json

# Bedrock Flow Runtime 클라이언트 생성
client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# Flow 실행
response = client.invoke_flow(
    flowIdentifier="[YOUR_FLOW_ID]",
    flowAliasIdentifier="[YOUR_FLOW_ALIAS_ID]",
    inputs=[
        {
            "content": {
                "document": "정보보호의 개요에 대해 설명해줘"
            },
            "nodeName": "FlowInputNode",
            "nodeOutputName": "document" 
        }
    ],
    enableTrace=False
)

# 결과 출력
result = {}
for event in response["responseStream"]:
    result.update(event)

print(json.dumps(result, ensure_ascii=False, indent=2))
