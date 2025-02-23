import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
 
from typing import List, Optional, TypedDict, Annotated
 
class LightModel(TypedDict):
   id: int
   name: str
   is_on: Optional[bool]
   brightness: Optional[int]
   hex: Optional[str]
 
class LightsPlugin:
   lights: List[LightModel] = [
      {"id": 1, "name": "Table Lamp", "is_on": False, "brightness": 100, "hex": "FF0000"},
      {"id": 2, "name": "Porch light", "is_on": False, "brightness": 50, "hex": "00FF00"},
      {"id": 3, "name": "Chandelier", "is_on": True, "brightness": 75, "hex": "0000FF"},
   ]
 
   @kernel_function(
      name="get_lights",
      description="Gets a list of lights and their current state",
   )
   async def get_lights(self) -> Annotated[List[LightModel], "An array of lights"]:
      """Gets a list of lights and their current state."""
      return self.lights
 
   @kernel_function(
      name="get_state",
      description="Gets the state of a particular light",
   )
   async def get_state(
      self,
      id: Annotated[int, "The ID of the light"]
   ) -> Annotated[Optional[LightModel], "The state of the light"]:
      """Gets the state of a particular light."""
      for light in self.lights:
         if light["id"] == id:
               return light
      return None
 
   @kernel_function(
      name="change_state",
      description="Changes the state of the light",
   )
   async def change_state(
      self,
      id: Annotated[int, "The ID of the light"],
      new_state: LightModel
   ) -> Annotated[Optional[LightModel], "The updated state of the light; will return null if the light does not exist"]:
      """Changes the state of the light."""
      for light in self.lights:
         if light["id"] == id:
               light["is_on"] = new_state.get("is_on", light["is_on"])
               light["brightness"] = new_state.get("brightness", light["brightness"])
               light["hex"] = new_state.get("hex", light["hex"])
               return light
      return None
   
 
import asyncio
import os
from dotenv import load_dotenv, dotenv_values
 
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
 
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.prompt_template.input_variable import InputVariable
from dotenv import dotenv_values

config = dotenv_values("Configuration.env")
 
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
 
async def main():
   load_dotenv()
   # Initialize the kernel
   kernel = Kernel()
 
   # Add Azure OpenAI chat completion
   kernel.add_service(
    AzureChatCompletion(
        deployment_name=config["AZURE_OPENAI_TEXT_DEPLOYMENT_NAME"],
        api_key=config["AZURE_OPENAI_API_KEY"],
        api_version=config["AZURE_OPENAI_API_VERSION"],
        endpoint=config["AZURE_OPENAI_ENDPOINT"]
   ))
 
   # Add a plugin (the LightsPlugin class is defined below)
   kernel.add_plugin(
      LightsPlugin(),
      plugin_name="Lights",
   )
 
   chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)
 
   # Enable planning
   execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
   execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})
   #execution_settings = AzureChatPromptExecutionSettings(
    #    service_id="default",
    #    ai_model_id="gpt-35-turbo",
    #    max_tokens=2000,
    #    temperature=0.7,)
   
   
 
   # Create a history of the conversation
   history = ChatHistory()
   history.add_system_message("What is the current state of the light?")
 
   # Get the response from the AI
   result = (await chat_completion.get_chat_message_contents(
      chat_history=history,
      settings=execution_settings,
      kernel=kernel,
      arguments=KernelArguments(),
   ))[0]
 
   # Print the results
   print("Assistant > " + str(result))
 
   # Add the message from the agent to the chat history
   history.add_message(result)
 
if __name__ == "__main__":
    asyncio.run(main())