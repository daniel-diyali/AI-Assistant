# The following program create an AI assistant that suggests restaurants.
# https://platform.openai.com/docs/assistants/tools/function-calling/quickstart?context=streaming
from typing_extensions import override
from openai import OpenAI, AssistantEventHandler
import json

client = OpenAI(
    api_key="API key"
)

open_file = open("test_user.json", "rb")

data_file = client.files.create(
    file=open_file,
    purpose='assistants'
)

ai_assistant = client.beta.assistants.create(
    name="Health and Fitness Advisor",
    instructions="You are an application with special expertise in Health and Fitness. If you can't find any data on the database, then you'll ask the user for information"
                    " Depending on the fitness goal, age, " +
                   "height, and weight, you are required to provide a specific fitness plan, provide a " +
                   "meal plan and nutrition advice, and suggest a few mindfulness exercises and mental health tips." +
                   " You are required to provide detailed information on the workouts on each specific days, " +
                   "including the specific type of workout, the length or the amount of sets and reps, and the meal plan.",
    model="gpt-3.5-turbo",
    tools=[{"type": "file_search"},
            { # --------------------- Edit this function to execute custom code ---------------------
              "type": "function",
              "function": {
                "name": "add_user", # name/id of tool like get_current_temperature
                "description": "Adds a user to the database",
                "parameters": { # Different text that you want chatgpt to give. (like name of user)
                  "type": "object",
                  "properties": {
                    "name": {
                      "type": "string",
                      #"enum": ["Command 1", "Command 2"],      can be used to constrict the input
                      "description": "Name of user "
                    }, # You can add more here
                    "fitnessgoal": {
                      "type": "string",
                      "description": "what the user wants to achieve"
                    },
                    "age": {
                      "type": "string",
                      "description": "age of the user"
                    },
                    "weight": {
                      "type": "string",
                      "description": "weight of the user"
                    },
                    "height": {
                      "type": "string",
                      "description": "height of the user. ex: \"5'9\", \"6'0\""
                    }
                  },
                  "required": ["name", "fitnessgoal", "age", "weight", "height"]
                }
              }
            },  # --------------------- Add more functions here ---------------------
{ # --------------------- Edit this function to execute custom code ---------------------
              "type": "function",
              "function": {
                "name": "modify_user", # name/id of tool like get_current_temperature
                "description": "Needs name to modify a user in the database",
                "parameters": { # Different text that you want chatgpt to give. (like name of user)
                  "type": "object",
                  "properties": {
                    "name": {
                      "type": "string",
                      #"enum": ["Command 1", "Command 2"],      can be used to constrict the input
                      "description": "Name of user "
                    }, # You can add more here
                    "fitnessgoal": {
                      "type": "string",
                      "description": "what the user wants to achieve"
                    },
                    "age": {
                      "type": "string",
                      "description": "age of the user"
                    },
                    "weight": {
                      "type": "string",
                      "description": "weight of the user"
                    },
                    "height": {
                      "type": "string",
                      "description": "height of the user. ex: \"5'9\", \"6'0\""
                    }
                  },
                  "required": ["name"]
                }
              }
            },
           ]
)

thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "This is the database of users",
            "attachments": [
                {"file_id": data_file.id, "tools": [{"type": "file_search"}]}
            ]
        }
    ]
)

print("\n############################################")
print("Thread id: " + thread.id)
print("Assistant id: " + ai_assistant.id)
print("############################################\n")


# --------------------- Add code functions here ---------------------
def add_user(name, fitnessgoal, age, weight, height):
    try:
        file_path = "test_user.json"

        # The new column to add
        new_data = {
            "name": name,
            "fitness goal": fitnessgoal,
            "age": age,
            "weight": weight,
            "height": height,
        }

        # Read the existing data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # May need to be changed to where your data is held
        data.get("test_user").append(new_data)

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent = 2)

        print("New entry added to database")
        return "success"

    # If file doesn't exist it will log the error and nothing will happen
    except Exception as e:
        print(f"An error occurred: {e}")
        return "failure"

def modify_user(name, fitnessgoal, age, weight, height):
    # Write code to override database if user changes something
    #try:
        file_path = "test_user.json"

        # The new column to add
        new_data = {
            "name": name,
            "fitness goal": fitnessgoal,
            "age": age,
            "weight": weight,
            "height": height,
        }

        # Read the existing data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
        i = 0
        for entry in data.get("test_user"):
            if entry.get("name") == name:
                break
            i += 1

        if i == len(data.get("test_user")):
            return "error user not found"

        # May need to be changed to where your data is held
        if fitnessgoal is not None:
            data.get("test_user")[i]["fitness goal"] = fitnessgoal
        if age is not None:
            data.get("test_user")[i]["age"] = int(age)
        if weight is not None:
            data.get("test_user")[i]["weight"] = float(weight)
        if height is not None:
            data.get("test_user")[i]["height"] = height

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent = 2)

        print("New entry added to database")
        return "success"

    # If file doesn't exist it will log the error and nothing will happen
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     return "failure"


# May need to import AssistantEventHandler from openai and override from typing_extensions
class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        # Retrieve events that are denoted with 'requires_action'
        # since these will have our tool_calls
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        # Here is where you will be checking what tools were called
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            # Loads function arguments
            function_args = json.loads(tool.function.arguments)

            # --------------------- Executes code here ---------------------
            if tool.function.name == "add_user":
                add_user(
                    name=function_args.get("name"), # Gets the parameter from ChatGPT
                    fitnessgoal=(function_args.get("fitnessgoal")), # If optional parameter second argument in get is default
                    age=int(function_args.get("age")),
                    weight=float(function_args.get("weight")),
                    height=(function_args.get("height"))
                )
                tool_outputs.append({"tool_call_id": tool.id, "output": ""})

            if tool.function.name == "modify_user":
                modify_user(
                    name=function_args.get("name"), # Gets the parameter from ChatGPT
                    fitnessgoal=(function_args.get("fitnessgoal", None)), # If optional parameter second argument in get is default
                    age=(function_args.get("age", None)),
                    weight=(function_args.get("weight", None)),
                    height=(function_args.get("height", None))
                )
                tool_outputs.append({"tool_call_id": tool.id, "output": ""})
        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with client.beta.threads.runs.submit_tool_outputs_stream(
                thread_id=self.current_run.thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs,
                event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()

# Different way of running prompt
with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=ai_assistant.id,
    event_handler=EventHandler()
) as stream:
    stream.until_done()

end = False

while not end:

    prompt = input("Enter a prompt: ")

    if prompt.lower() == "goodbye":
        print("Have a good day!")
        break

    client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=prompt
    )

    # Different way of running prompt
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=ai_assistant.id,
        event_handler=EventHandler()
    ) as stream:
        stream.until_done()



    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print("Assistant: " + messages.data[0].content[0].text.value)


