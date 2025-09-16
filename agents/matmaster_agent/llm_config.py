from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from opik.integrations.adk import OpikTracer
import os

load_dotenv()

MODEL_MAPPING = {
    ('openai', 'gpt-4o-mini'): 'openai/gpt-4o-mini',
    ('openai', 'gpt-4o'): 'openai/gpt-4o',
    ('openai', 'o3-mini'): 'openai/o3-mini',
    ('openai', 'gemini2.5-pro'): 'openai/gemini-2.5-pro-preview-03-25',
    ('openai', 'gemini-2.5-pro-preview-05-06'): 'openai/gemini-2.5-pro-preview-05-06',
    ('openai', 'deepseek-r1'): 'openai/deepseek-r1',
    ('openai', 'claude-sonnet-4-20250514'): 'openai/claude-sonnet-4-20250514',
    ('openai', 'gemini-2.5-flash-preview-05-20'): 'openai/gemini-2.5-flash-preview-05-20',
    ('openai', 'qwen-plus'): 'openai/qwen-plus',
    ('openai', 'gpt-5'): 'openai/gpt-5',
    ('openai', 'gpt-5-nano'): 'openai/gpt-5-nano',
    ('openai', 'gpt-5-mini'): 'openai/gpt-5-mini',
    ('openai', 'gpt-5-chat'): 'openai/gpt-5-chat',
    ('azure', 'gpt-4o'): 'azure/gpt-4o',
    ('azure', 'gpt-4o-mini'): 'azure/gpt-4o-mini',
    ('litellm_proxy', 'gemini-2.0-flash'): 'litellm_proxy/gemini-2.0-flash',
    ('litellm_proxy', 'gemini-2.5-flash'): 'litellm_proxy/gemini-2.5-flash',
    ('litellm_proxy', 'gemini-2.5-pro'): 'litellm_proxy/gemini-2.5-pro',
    ('litellm_proxy', 'claude-sonnet-4'): 'litellm_proxy/claude-sonnet-4',
    ('azure', 'gpt-5'): 'azure/gpt-5',
    ('litellm_proxy', 'gpt-5-mini'): 'litellm_proxy/azure/gpt-5-mini',
    ('litellm_proxy', 'gpt-5-nano'): 'litellm_proxy/azure/gpt-5-nano',
    ('azure', 'gpt-5-chat'): 'azure/gpt-5-chat',
    # ("gemini", "gemini1.5-turbo"): "gemini/gemini1.5-turbo",
    # ("gemini", "gemini2.5-pro"): "gemini/gemini-2.5-pro-preview-03-25",
    # ("deepseek", "deepseek-reasoner"): "deepseek/deepseek-reasoner",
    ('deepseek', 'deepseek-chat'): 'deepseek/deepseek-chat',
    ('volcengine', 'deepseek-chat'): 'volcengine/ep-20250210170324-dd9g4',
    ('volcengine', 'deepseek-R1-0528'): 'volcengine/ep-20250612143101-qf6n8',
    ('volcengine', 'deepseek-Seed-1.6'): 'volcengine/ep-20250627140204-clmmm',
    ('volcengine', 'Doubao-Seed-1.6-flash'): 'volcengine/ep-20250627141116-z2fv4',
    ('volcengine', 'Doubao-Seed-1.6-thinking'): 'volcengine/ep-20250627141021-h4wch'
}

# DEFAULT_MODEL = "azure/gpt-4o-mini"
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'azure/gpt-4o-mini')


class LLMConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        openai_provider = 'openai'
        azure_provider = 'azure'
        litellm_provider = 'litellm_proxy'
        deepseek_provider = 'deepseek'
        volcengine_provider = 'volcengine'

        gpt_4o = 'gpt-4o'
        gpt_4o_mini = 'gpt-4o-mini'
        gemini_2_5_flash = 'gemini-2.5-flash'
        gemini_2_0_flash = 'gemini-2.0-flash'
        gemini_2_5_pro = 'gemini-2.5-pro'
        claude_sonnet_4 = 'claude-sonnet-4'
        deepseek_chat = 'deepseek-chat'
        gpt_5 = 'gpt-5'
        gpt_5_nano = 'gpt-5-nano'
        gpt_5_mini = 'gpt-5-mini'
        gpt_5_chat = 'gpt-5-chat'

        # Helper to init any provider model
        def _init_model(provider_key: str, model_name: str):
            return LiteLlm(model=MODEL_MAPPING.get((provider_key, model_name), DEFAULT_MODEL))

        self.gpt_4o_mini = _init_model(azure_provider, gpt_4o_mini)
        self.gpt_4o = _init_model(azure_provider, gpt_4o)
        self.gemini_2_0_flash = _init_model(litellm_provider, gemini_2_0_flash)
        self.gemini_2_5_flash = _init_model(litellm_provider, gemini_2_5_flash)
        self.gemini_2_5_pro = _init_model(litellm_provider, gemini_2_5_pro)
        self.claude_sonnet_4 = _init_model(litellm_provider, claude_sonnet_4)
        self.deepseek_chat = _init_model(deepseek_provider, deepseek_chat)

        # GPT-5 models
        self.gpt_5 = _init_model(azure_provider, gpt_5)
        self.gpt_5_nano = _init_model(litellm_provider, gpt_5_nano)
        self.gpt_5_mini = _init_model(litellm_provider, gpt_5_mini)
        self.gpt_5_chat = _init_model(azure_provider, gpt_5_chat)

        # tracing
        self.opik_tracer = OpikTracer()

        self._initialized = True


def create_default_config() -> LLMConfig:
    return LLMConfig()


MatMasterLlmConfig = create_default_config()
