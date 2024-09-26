import json
from Utils import BaseErrorCodes, log_meta_custom_decorator, SolutionBaseException, log_meta_custom_decorator_func
from LLMObject import GenAITextGenerator
import traceback


# Function to generate a detailed prompt for LLM based on column details
def generate_llm_prompt(table_details):
    """
    Generate a detailed prompt for the LLM to generate synthetic data based on the table details.

    Parameters:
    table_details (dict): The details of the table for which to generate the LLM prompt.

    Returns:
    str: A detailed prompt for the LLM.
    """
    col_prompt = ""
    description = table_details["description"]
    name = table_details["dataset"]

    for property in table_details['properties']:
        col_prompt += f"- attribute:{property['name']} attribute name:{property['label']} Type:{property['type']} Description:{property['description']}\n"

    # prompt += "\nPlease generate a synthetic dataset in json format which would be array of key value pair, where key is the attribute and value is value, ensuring that the values conform to the descriptions and constraints provided for each column. The data should mimic the distribution, range, and format as closely as possible to real-world data. Ensure that referential integrity is maintained where applicable, and include a variety of values within the allowed constraints to reflect realistic data variability.\n"

    return col_prompt, description, name
    
    

def format_prompt(prompt_template:str, input_param:dict):
    return prompt_template.format(**input_param)
    

@log_meta_custom_decorator(BaseErrorCodes.CLIENT_INPUT_ERROR)
def build_genai_input(event):
    # Extract the necessary information from the event
    llm_prompt_config = event.get('llm_prompt_config')
    llm_tuning_parameters = event.get('llm_tuning_parameters')
    dataset = event.get('dataset')

    # Extract Bedrock model details
    model = llm_prompt_config['gen_model_config']['model']
    region = llm_prompt_config['gen_model_config']['region']
    prompt_template = llm_prompt_config['prompts']['SYNTHETIC_DATA_GEN']['full_prompt']
    
    # Get table prompt
    col_prompt, table_desc, table_name = generate_llm_prompt(dataset)
    
    # Get the format for synthetic data, if nothing is mentioned then default is json
    gen_format = llm_prompt_config['prompts']['SYNTHETIC_DATA_GEN'].get("format", "json")
    gen_items_count = llm_prompt_config['prompts']['SYNTHETIC_DATA_GEN'].get("gen_item_count", 5)

    # Combine prompt with dataset details
    prompt_params =  {
            "dataset_name"       :table_name,
            "dataset_description":table_desc,
            "col_prompt"         :col_prompt,
            "items_count"        :gen_items_count,
            "format"             :gen_format
            
        }
    return model, region, llm_tuning_parameters, prompt_template, prompt_params  


@log_meta_custom_decorator_func(BaseErrorCodes.JSON_OUTPUT_PARSER_ERROR)
def parser_gen_text_to_json(generated_text):
    # json.loads(res.get('outputs')[0]['text'].replace("\\_", "_"))
    # generated_text.get('outputs')[0]['text']
    try:
        text = generated_text.get('outputs')[0]['text']
        p = json.loads(text.replace("\\_", "_"))
        return p
    except Exception as e:
        raise Exception(f'''
            Error raised is {e}
            Generated text is:
            {generated_text}
        ''')


@log_meta_custom_decorator_func(BaseErrorCodes.GENERATION_ERROR)
def validateGeneratedText(response):
    stop_reason = response.get('outputs')[0]['stop_reason']

    if not stop_reason == "stop":
        raise Exception(f"Response generation from the either incomplete or faulty. Because: {stop_reason}")


def lambda_handler(event, context):
    # TODO implement
    # with open("data/inputmock.json", "r") as f:
    #     data = json.loads(f.read())

    try:
        model, region, llm_tuning_parameters, prompt_template, prompt_params = build_genai_input(event)

        input_params = {
            "prompt_template": prompt_template,
            "params": prompt_params,
            **llm_tuning_parameters,
            "model_id": model
        }

        # print(f'''
        #     Model: {model}
        #     params: {llm_tuning_parameters}
        #     prompt: {formatted_prompt}
        # ''')
        text_generator = GenAITextGenerator(**input_params)
        # print('''
        #     "HERE GENERATE PROMPT"
        # ''')
        # print(text_generator.prompt)

        generated_text = text_generator.generate_text()

        # Will raise exception if LLM is incomplete
        validateGeneratedText(generated_text)

        # print("\n")

        gen_response_json = parser_gen_text_to_json(generated_text)
        
        return {
            'statusCode': 200,
            'status': 'SUCCESS',
            'prompt':text_generator.prompt,
            'body': gen_response_json
        }
    
            # f"Error Code: {self.error_response.error_code}, "
            # f"Error Name: {self.error_response.error_name}, "
            # f"Message: {self.error_response.error_message}, "
            # f"Reason: {self.error_response.error_reason}, "
            # f"Technical Description: {self.error_response.technical_error_description or 'N/A'}"    
    except SolutionBaseException as e:
        return {
            'statusCode': e.error_response.error_code,
            'status': 'FAILED',
            'body': {
                'prompt':text_generator.prompt,
                'error_message':e.error_response.error_message,
                'error_name':e.error_response.error_name,
                'error_code':e.error_response.error_code,
                'error_reason':e.error_response.error_reason,
                'technical_error_description':traceback.format_exc(),
                }
        }
    

def lambda_handler_v1():
    # TODO implement
    with open("data/inputmock.json", "r") as f:
        data = json.loads(f.read())

    try:
        model, region, llm_tuning_parameters, prompt_template, prompt_params = build_genai_input(data)

        input_params = {
            "prompt_template": prompt_template,
            "params": prompt_params,
            **llm_tuning_parameters,
            "model_id": model
        }

        # print(f'''
        #     Model: {model}
        #     params: {llm_tuning_parameters}
        #     prompt: {formatted_prompt}
        # ''')
        text_generator = GenAITextGenerator(**input_params)
        print('''
            "HERE GENERATE PROMPT"
        ''')
        print(text_generator.prompt)

        generated_text = text_generator.generate_text()

        print('''
            Here is the generated output
        ''')

        validateGeneratedText(generated_text)

        # print(generated_text)

        print("\n")

        gen_response_json = parser_gen_text_to_json(generated_text)
        
        return {
            'statusCode': 200,
            'status': 'SUCCESS',
            'body': gen_response_json
        }
    
            # f"Error Code: {self.error_response.error_code}, "
            # f"Error Name: {self.error_response.error_name}, "
            # f"Message: {self.error_response.error_message}, "
            # f"Reason: {self.error_response.error_reason}, "
            # f"Technical Description: {self.error_response.technical_error_description or 'N/A'}"    
    except SolutionBaseException as e:
        trace_string = traceback.format_exc()
        print('''

                Exception is raised
        ''')
        return {
            'statusCode': e.error_response.error_code,
            'status': 'FAILED',
            'body': {
                'error_message':e.error_response.error_message,
                'error_name':e.error_response.error_name,
                'error_code':e.error_response.error_code,
                'error_reason':e.error_response.error_reason,
                'technical_error_description':e.error_response.technical_error_description,
                }
        }

if __name__ == "__main__":
    print(lambda_handler_v1())