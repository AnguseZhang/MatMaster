from pydantic import BaseModel
from pathlib import Path
from langchain_core.tools import tool
from loguru import logger
from pprint import pprint
from typing import Optional

class AbacusPrepareInput(BaseModel):
    stru_file: Path
    stru_type: str
    job_type: str
    lcao: bool
    nspin: int
    soc: bool
    dftu: bool
    dftu_param: Optional[dict]
    init_mag: Optional[dict]
    afm: Optional[bool]
    extra_input: Optional[dict]
    name: Optional[str]

def abacus_prepare(input: AbacusPrepareInput):
    pprint(input.model_dump())
    return "abacus_prepare"

@tool
def abacus_prepare_tool(
    stru_file: Path,
    stru_type: str,
    job_type: str,
    lcao: bool,
    nspin: int,
    soc: bool,
    dftu: bool,
    dftu_param: dict = {},
    init_mag: dict = {},
    afm: bool = False,
    extra_input: dict = {},
    name: str = "",
):
    """
    Prepare ABACUS input file directory from structure file and provided information.
    """
    input = AbacusPrepareInput(
        stru_file=stru_file,
        stru_type=stru_type,
        job_type=job_type,
        lcao=lcao,
        nspin=nspin,
        soc=soc,
        dftu=dftu,
        dftu_param=dftu_param,
        init_mag=init_mag,
        afm=afm,
        extra_input=extra_input,
        name=name,
    )
    return abacus_prepare(input)

if __name__ == "__main__":
    input_dict = {
        "stru_file": "./demo.cif",
        "stru_type": "cif",
        "job_type": "scf",
        "lcao": True,
        "nspin": 1,
        "soc": False,
        "dftu": True,
    }
    res = abacus_prepare_tool.invoke(input_dict)
    print(res)