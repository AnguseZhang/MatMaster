from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from opik.integrations.adk import OpikTracer

load_dotenv()

SUPPORTED_PROVIDERS = ["openai", "deepseek", "gemini", "azure"]
# "anthropic", "perplexity", "huggingface", "local", "azureopenai"

MODEL_MAPPING = {
    ("openai", "gpt-4o-mini"): "openai/gpt-4o-mini",
    ("openai", "gpt-4o"): "openai/gpt-4o",
    ("openai", "o3-mini"): "openai/o3-mini",
    ("openai", "gemini2.5-pro"): "openai/gemini-2.5-pro-preview-03-25",
    ("openai", "gemini-2.5-pro-preview-05-06"): "openai/gemini-2.5-pro-preview-05-06",
    ("openai", "deepseek-r1"): "openai/deepseek-r1",
    ("openai", "claude-sonnet-4-20250514"): "openai/claude-sonnet-4-20250514",
    ("openai", "gemini-2.5-flash-preview-05-20"): "openai/gemini-2.5-flash-preview-05-20",
    ("azure", "gpt-4o"): "azure/gpt-4o",
    ("litellm_proxy", "gemini-2.0-flash"): "litellm_proxy/gemini-2.0-flash",
    ("litellm_proxy", "gemini-2.5-flash"): "litellm_proxy/gemini-2.5-flash",
    # ("litellm_proxy", "gemini-2.5-pro"): "litellm_proxy/gemini/gemini-2.5-pro",
    ("litellm_proxy", "gemini-2.5-pro"): "litellm_proxy/gemini-2.5-pro-preview-06-05",
    ("litellm_proxy", "claude-sonnet-4"): "litellm_proxy/claude-sonnet-4",
    # ("gemini", "gemini1.5-turbo"): "gemini/gemini1.5-turbo",
    # ("gemini", "gemini2.5-pro"): "gemini/gemini-2.5-pro-preview-03-25",
    # ("deepseek", "deepseek-reasoner"): "deepseek/deepseek-reasoner",
    ("deepseek", "deepseek-chat"): "deepseek/deepseek-chat",
}

DEFAULT_MODEL = "azure/gpt-4o-mini"

DB_NAMES = {
    'polymer': 'polymer_db',
    'electrolyte': 'electrolyte_db', 
    'solid_electrolyte': 'solid_electrolyte_db',
    'default': 'polymer_db'  
}


class LLMConfig(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        gpt_provider = "azure"
        litellm_provider = "litellm_proxy"
        deepseek_provider = "deepseek"

        gpt_4o = "gpt-4o"
        gemini_2_5_flash = "gemini-2.5-flash"
        gemini_2_0_flash = "gemini-2.0-flash"
        gemini_2_5_pro = "gemini-2.5-pro"
        claude_sonnet_4 = "claude-sonnet-4"

        deepseek_chat = 'deepseek-chat'

        # Helper to init any provider model
        def _init_model(provider_key: str, model_name: str):
            return LiteLlm(
                model=MODEL_MAPPING.get(
                    (provider_key, model_name),
                    DEFAULT_MODEL
                )
            )

        # Helper to get database name
        def _init_database(db_type: str = 'default'):
            return DB_NAMES.get(db_type, DB_NAMES['default'])

        self.gpt_4o = _init_model(gpt_provider, gpt_4o)
        self.gemini_2_0_flash = _init_model(litellm_provider, gemini_2_0_flash)
        self.gemini_2_5_flash = _init_model(litellm_provider, gemini_2_5_flash)
        self.gemini_2_5_pro = _init_model(litellm_provider, gemini_2_5_pro)
        self.claude_sonnet_4 = _init_model(litellm_provider, claude_sonnet_4)
        self.deepseek_chat = _init_model(deepseek_provider, deepseek_chat)

        # tracing
        self.opik_tracer = OpikTracer()
        
        # database configuration
        self.polymer_db = _init_database('polymer')
        self.electrolyte_db = _init_database('electrolyte')
        self.solid_electrolyte = _init_database('solid_electrolyte')

        self._initialized = True


def create_default_config() -> LLMConfig:
    return LLMConfig()


MatMasterLlmConfig = create_default_config()