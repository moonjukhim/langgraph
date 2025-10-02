import io
import random

import boto3
import matplotlib.pyplot as plt
import streamlit as st

AGENT_ID = "BNVV2KBP8Z"
REGION = "us-east-1"
IMAGE_FOLDER = "images"

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=REGION,
)

bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime", region_name=REGION
)


def generate_random_15digit():
    number = ""

    for _ in range(15):
        number += str(random.randint(0, 9))

    return number


def invoke_bedrock_agent(inputText, sessionId, trace_container, endSession=False):
    # Invoke the Bedrock agent with the given input text
    response = bedrock_agent_runtime.invoke_flow(
        flowIdentifier="BNVV2KBP8Z",
        flowAliasIdentifier="TSTALIASID",
        inputs = [
            { 
                "content": { 
                    "document": inputText
                },
                "nodeName": "FlowInputNode",
                "nodeOutputName": "document"
            }
        ]
    )


    # Get the event stream from the response
    event_stream = response["responseStream"]

    model_response = {"text": "", "images": [], "files": [], "traces": []}
    

    # Process each event in the stream
    for index, event in enumerate(event_stream):
        print(f"Event {index}:")
        print(str(event))
        print("\n")

        try:
            
            # Handle text chunks
            if index == 0:
                text = event["flowOutputEvent"]["content"]["document"]
                model_response["text"] += text
                return model_response


            # Handle file outputs
            if "files" in event:
                print("Files received")
                files = event["files"]["files"]
                for file in files:
                    name = file["name"]
                    type = file["type"]
                    bytes_data = file["bytes"]

                    # Display PNG images using matplotlib
                    if type == "image/png":

                        # save image to disk
                        img = plt.imread(io.BytesIO(bytes_data))
                        img_name = f"{IMAGE_FOLDER}/{name}"
                        plt.imsave(img_name, img)

                        # if image name not in images
                        if img_name not in model_response["images"]:
                            model_response["images"].append(img_name)
                        print(f"Image '{name}' saved to disk.")
                    # Save other file types to disk
                    else:
                        with open(name, "wb") as f:
                            f.write(bytes_data)
                            model_response["files"].append(name)
                        print(f"File '{name}' saved to disk.")
        except Exception as e:
            print(f"Error processing event: {e}")
            continue