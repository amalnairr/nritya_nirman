import autogen
from typing import Annotated

config_list = autogen.config_list_from_json("GROQ_CONFIG_LIST.json")

llm_config = {
    "temperature": 0.15,
    "config_list": config_list,
    "max_tokens": 800,
}

user_proxy = autogen.UserProxyAgent(
    name = "Admin",
    system_message = "Human Admin. The process ends only if the Admin approves. Admin approves if critic approves.",
    human_input_mode = "NEVER",
    code_execution_config={"use_docker": False},
)

with open("Tukda.txt", "r") as f:
    tukda = f.read()
with open("Tihai.txt", "r") as f:
    tihai = f.read()
with open("SamSeSam.txt", "r") as f:
    samse = f.read()
with open("Chakkardar.txt", "r") as f:
    chakkardar = f.read()
with open("GenRules.txt", "r") as f:
    rules = f.read()

tihai_composer = autogen.ConversableAgent(
    name = "tihai_composer",
    llm_config = llm_config,
    description="This is a composer agent that generates Kathak Tihai compositions.",
    system_message = """Tihai Composer. You compose  a variety of unique Kathak Tihais. Each segment is separated by a pipe symbol (|).
    Take the feedback of the critic and make changes if needed.
    Some examples of Kathak Tihais: {tihai}""".format(tihai=tihai),
)

tukda_composer = autogen.ConversableAgent(
    name = "tukda_composer",
    llm_config = llm_config,
    description="This is a composer agent that generates Kathak Tukda compositions.",
    system_message = """Tukda Composer. You compose Kathak Tukdas only and nothing else. Each segments is separated by a pipe (|).
    Some examples of Kathak Tukdas: {tukda}
    Take the feedback of the critic and make changes if needed.""".format(tukda=tukda),
)

chakkardar_composer = autogen.ConversableAgent(
    name = "ChakkardarComp",
    llm_config = llm_config,
    description="This is a composer agent that generates Kathak Chakkardar compositions.",
    system_message = """Chakkardar Composer. You compose Kathak Chakkardar Tukdas only and nothing else. Each segments is separated by a pipe (|).
    Some examples of Chakkardar compositions: {chakkardar}
    Take the feedback of the critic and make changes if needed.""".format(chakkardar=chakkardar),
)

samsesam_composer = autogen.ConversableAgent(
    name = "SamSeSamComp",
    llm_config = llm_config,
    description="This is a composer agent that generates Kathak Sam Se Sam compositions.",
    system_message = """Chakkardar Composer. You compose Kathak Chakkardar Tukdas only and nothing else. Each segments is a segment, and each segment is separated by a pipe symbol (|). Each segment contains bols. 
    Some examples of Kathak compositions: {samse}
    Take the feedback of the critic and make changes if needed.""".format(samse=samse),
)

def segments_counts(composition: Annotated[str, "The composition to check"]) -> int:
    return composition.count("|") + 1

critic = autogen.ConversableAgent(
    name = "Rule Checker",
    llm_config = llm_config,
    description="This is a critic agent that checks the rules of the Kathak compositions.",
    system_message = """Check the Kathak compositions generated by the composer. 
    Ensure that the compositions follow the rules of Kathak dance. Provide feedback to the composer
    Do not generate compositions. If the composition is correct end message with "APPROVED".
    Here are some rules: {rules}""".format(rules=rules),
    is_termination_msg=lambda x: "APPROVED" in x['content'] if x['content'] else False,
)

# critic.register_for_llm(name = 'segments_counts', description="Count the number of segmentss in the composition")(segments_counts)
# critic.register_for_execution(name = 'segments_counts')(segments_counts)

segments_counter = autogen.ConversableAgent(
    name = "Segments Counter",
    llm_config = llm_config,
    description="This is a critic agent that checks the number of segmentss in the Kathak compositions.",
    system_message = """Check the Kathak compositions generated by the composer and count the number of segmentss in the composition.
    Do not generate compositions. Provide feedback to the critic directly."""
)

autogen.register_function(segments_counts, caller = critic, executor=segments_counter, name = "segments_counter", description="Count the number of segments in the composition")

group_chat = autogen.GroupChat(
    agents = [tukda_composer, critic, user_proxy, segments_counter], messages = [], max_round = 10,
)

manager = autogen.GroupChatManager(
    groupchat = group_chat, llm_config = llm_config

    )

user_proxy.initiate_chat(
    manager,
    message = """
    Compose a Kathak Tukda that starts with tat.
    """
    )

