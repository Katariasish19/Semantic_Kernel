import asyncio
import requests
import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from dotenv import dotenv_values
from typing import Annotated

config = dotenv_values("Config.env")

class WeatherPlugin:
    """A plugin that provides weather information for cities."""

    @kernel_function(name="get_weather", description="Get the weather for a city")
    def get_weather(city: str) -> str:
        api_key = config["OPENWEATHERMAP_API_KEY"]
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"The current weather in {city} is {description} with a temperature of {temp}°C."
        else:
            return f"Failed to get weather data for {city}."

async def main():
    # Initialize the kernel
    kernel = Kernel()

    # Add Azure OpenAI chat completion
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=config["AZURE_OPENAI_TEXT_DEPLOYMENT_NAME"],
            api_key=config["AZURE_OPENAI_API_KEY"],
            api_version=config["AZURE_OPENAI_API_VERSION"],
            endpoint=config["AZURE_OPENAI_ENDPOINT"]
        )
    )

    # Add the WeatherPlugin to the kernel
    kernel.add_plugin(
        WeatherPlugin(),
        plugin_name="weather"
    )

    chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
    execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})

    # Create a history of the conversation
    history = ChatHistory()
    history.add_system_message("You are a helpful assistant that provides weather information.")
    history.add_user_message("What is the weather like in Sydney?")
    history.add_assistant_message('To use the tool, please provide the city for which you want weather information in the following format: `{"city": "CityName"}`')
    history.add_user_message('{"city": "Sydney"}')

    # Get the response from the AI
    result = (await chat_completion.get_chat_message_contents(
        chat_history=history,
        settings=execution_settings,
        kernel=kernel,
        arguments=KernelArguments(),
    ))[0]

    # Print the results
    print("Assistant > " + str(result))

if __name__ == "__main__":
    asyncio.run(main())