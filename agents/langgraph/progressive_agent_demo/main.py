"""
agent 调用一个复杂参数的工具 abacus_prepare，然后用 progressive 的方式进行优化参数填写的例子

"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path
from loguru import logger

load_dotenv()

from langchain_openai import AzureChatOpenAI
from mem0 import MemoryClient

memory_client = MemoryClient()



class AbacusPrepareInput(BaseModel):
    stru_file: Path
    stru_type: str
    job_type: str
    lcao: bool
    nspin: int
    soc: bool
    dftu: bool
    dftu_param: dict
    init_mag: dict
    afm: bool
    extra_input: dict
    name: str

def abacus_prepare(input: AbacusPrepareInput):
    logger.info(input)
    return "abacus_prepare"

def test_llm():
    deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    print(deployment_name)

    client = AzureChatOpenAI(
        deployment_name=deployment_name,
    )

    response = client.invoke("你是什么模型,告诉我你是 gpt-4 还是 gpt-5，精确版本号")

    print(response)


def test_bare_toolcall():
    data = {
        "stru_file": "./demo.cif",
        "stru_type": "cif",
        "job_type": "scf",
        "lcao": True,
        "nspin": 1,
        "soc": False,
        "dftu": True,
        "dftu_param": {"Fe": 7.0, "Ni": ("d", 4.0)},
        "init_mag": {"Fe": 2.0, "Ni": 2.0},
        "afm": False,
        "extra_input": {"smearing_sigma": 0.01, "dft_functional": "pbe"}
    }

    abacus_prepare(data) 


def test_mem0():
    # messages = [
    #     { "role": "user", "content": "Hi, I'm Ting. 我是中国人，我早晨习惯喝粥" },
    #     { "role": "assistant", "content": "你好，你是中国人，你早晨习惯喝粥，那我早晨会推荐你喝小米粥和八宝粥" }
    # ]

    # add_result = memory_client.add(messages, user_id="ting",  metadata={"category": "breakfast"}, output_format="v1.1")
    # print("add_result")
    # print(add_result)
    
    query = "What can I cook?"

    search_result = memory_client.search(
        query, 
        user_id="ting",
        metadata={"category": "breakfast"}
    )
    print("search_result")
    print(search_result)
    
    memories = memory_client.get_all(user_id="ting")
    print("all memories")
    print(memories)


    
def main():

    # test_llm()

    # test_bare_toolcall()

    test_mem0()
   


    
if __name__ == "__main__":
    main()

 