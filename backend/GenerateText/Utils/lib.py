"""
This is a utility python module
"""
__all__ = ["log_meta_custom_decorator", "log_meta_custom_decorator_func", "BaseErrorCodes", "SolutionBaseException"]

from pydantic import BaseModel
from enum import Enum
import functools
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BaseErrorCodes(Enum):
    AWS_SESSION_FAILED = (500, "AWSSessionFailed", "AWS Session creation failed")
    GENAI_RESPONSE_FAILED = (502, "GenAIResponseFailed", "Generative AI response generation failed")
    CLIENT_INPUT_ERROR = (400, "ClientInputError", "Client input is not correct")
    JSON_OUTPUT_PARSER_ERROR = (500, "JSONOutputParserError", "JSON parsing of the generated text failed")
    GENERATION_ERROR = (400, "GenerationError", "Response generation has errors")
    # Add more error codes as needed

    def __init__(self, code: int, id: str, desc: str):
        self.code = code
        self.id = id
        self.desc = desc
        
        
class BaseErrorResponse(BaseModel):
    error_message: str
    error_reason: str
    error_code: int
    error_name: str
    technical_error_description: str | None = None  # Optional field


class SolutionBaseException(Exception):

    def __init__(self, 
                 error_message: str, 
                 error_reason: str, 
                 error_code: int, 
                 error_name: str, 
                 technical_error_description: str | None = None):
        # Create APIErrorResponse object with the given parameters
        self.error_response = BaseErrorResponse(
            error_message=error_message,
            error_reason=error_reason,
            error_code=error_code,
            error_name=error_name,
            technical_error_description=technical_error_description
        )
        super().__init__(error_message)

    def __str__(self):
        return (
            f"Error Code: {self.error_response.error_code}, "
            f"Error Name: {self.error_response.error_name}, "
            f"Message: {self.error_response.error_message}, "
            f"Reason: {self.error_response.error_reason}, "
            f"Technical Description: {self.error_response.technical_error_description or 'N/A'}"
        )
        
        
# Define the parameterized decorator
def log_meta_custom_decorator(error: BaseErrorCodes):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__  # Get the class name
            method_name = func.__name__  # Get the method name
            logger.info(f"Calling {class_name}.{method_name} with args: {args[1:]}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)  # Call the actual method
                logger.info(f"{class_name}.{method_name} COMPLETED")
                return result
            except Exception as e:
                logger.info(f"{class_name}.{method_name} FAILED: {e}")
                raise SolutionBaseException(
                    error_message=error.desc,
                    error_reason=str(e),
                    error_code=error.code,
                    error_name=error.id,
                    technical_error_description="NA"
                )                
            # logger.info(f"{custom_message} - {class_name}.{method_name} returned: {result}")
        return wrapper
    return decorator


# Define the parameterized decorator
def log_meta_custom_decorator_func(error: BaseErrorCodes):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            method_name = func.__name__  # Get the method name
            logger.info(f"Calling {method_name} with args: {args[1:]}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)  # Call the actual method
                logger.info(f"{method_name} COMPLETED")
                return result
            except Exception as e:
                logger.info(f"{method_name} FAILED: {e}")
                raise SolutionBaseException(
                    error_message=error.desc,
                    error_reason=str(e),
                    error_code=error.code,
                    error_name=error.id,
                    technical_error_description="NA"
                )                
            # logger.info(f"{custom_message} - {class_name}.{method_name} returned: {result}")
        return wrapper
    return decorator