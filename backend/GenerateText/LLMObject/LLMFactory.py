__all__ = ["GenAITextGenerator"]

import boto3
import json
import boto3.session
from botocore.exceptions import ClientError
from Utils import BaseErrorCodes, log_meta_custom_decorator

class BedrockGenAIModel:

    @log_meta_custom_decorator(BaseErrorCodes.AWS_SESSION_FAILED)
    def __init__(self,
                 profile_name:str="bedrock-admin"
                 ):
        # boto3_session = boto3.session.Session(
        #     profile_name = "bedrock-admin"
        # )
        # self.bedrock_client = boto3_session.client('bedrock-runtime')

        self.bedrock_client = boto3.client('bedrock-runtime')


    @log_meta_custom_decorator(BaseErrorCodes.GENAI_RESPONSE_FAILED)
    def invoke_genai(   self,
                        prompt:str,
                        model_id:str = "mistral.mixtral-8x7b-instruct-v0:1",
                        max_tokens:int = 1000, 
                        temperature:float = 0.1, 
                        top_p:float = 0.7, 
                        top_k:float = 50
                    ):
        self.body = json.dumps({
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k
        })

        self.response = self.bedrock_client.invoke_model(
            body=self.body,
            # contentType='string',
            # accept='string',
            modelId='mistral.mixtral-8x7b-instruct-v0:1',
            # trace='ENABLED'|'DISABLED',
            # guardrailIdentifier='string',
            # guardrailVersion='string'
        )

        return self.body
    

    def response_text(self):
        return json.loads(self.response.get('body').read())

        

class GenAITextGenerator:

    def build_prompt(self, prompt_template:str, params:dict):
        return prompt_template.format(**params)
    

    def __init__(   self, 
                    prompt_template:str, 
                    params:dict,
                    model_id:str = "mistral.mixtral-8x7b-instruct-v0:1",
                    max_tokens:int = 1000, 
                    temperature:float = 0.1, 
                    top_p:float = 0.7, 
                    top_k:int = 50):
        
        self.genai_client = BedrockGenAIModel(profile_name = "bedrock-admin")
        self.prompt = self.build_prompt(prompt_template, params)
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k


    def generate_text(self):

        # logger.info("Generating text with Mistral AI model %s", model_id)

        # bedrock = boto3.client(service_name='bedrock-runtime')

        response = self.genai_client.invoke_genai(
            prompt=self.prompt,
            model_id = self.model_id,
            max_tokens = self.max_tokens, 
            temperature = self.temperature, 
            top_p = self.top_p, 
            top_k = self.top_k
        )

        # print(response)

        return self.genai_client.response_text()

