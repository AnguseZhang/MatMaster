import logging
import os

from dotenv import load_dotenv

from agents.matmaster_agent.constant import MATMASTER_AGENT_NAME

load_dotenv()
logger = logging.getLogger(__name__)

MODEL_MAPPING = {
    ('openai', 'gpt-4o-mini'): 'openai/gpt-4o-mini',
    ('openai', 'gpt-4o'): 'openai/gpt-4o',
    ('openai', 'o3-mini'): 'openai/o3-mini',
    ('openai', 'gemini2.5-pro'): 'openai/gemini-2.5-pro-preview-03-25',
    ('openai', 'gemini-2.5-pro-preview-05-06'): 'openai/gemini-2.5-pro-preview-05-06',
    ('openai', 'deepseek-r1'): 'openai/deepseek-r1',
    ('openai', 'claude-sonnet-4-20250514'): 'openai/claude-sonnet-4-20250514',
    (
        'openai',
        'gemini-2.5-flash-preview-05-20',
    ): 'openai/gemini-2.5-flash-preview-05-20',
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
    ('litellm_proxy', 'gemini-3-pro-preview'): 'litellm_proxy/gemini-3-pro-preview',
    ('litellm_proxy', 'claude-sonnet-4'): 'litellm_proxy/claude-sonnet-4',
    ('litellm_proxy', 'gpt-5'): 'litellm_proxy/azure/gpt-5',
    ('litellm_proxy', 'gpt-5-mini'): 'litellm_proxy/azure/gpt-5-mini',
    ('litellm_proxy', 'gpt-5-nano'): 'litellm_proxy/azure/gpt-5-nano',
    ('litellm_proxy', 'gpt-5-chat'): 'litellm_proxy/azure/gpt-5-chat',
    ('litellm_proxy', 'zh-gpt-5-chat'): 'litellm_proxy/zh-gpt-5-chat',
    # ("gemini", "gemini1.5-turbo"): "gemini/gemini1.5-turbo",
    # ("gemini", "gemini2.5-pro"): "gemini/gemini-2.5-pro-preview-03-25",
    # ("deepseek", "deepseek-reasoner"): "deepseek/deepseek-reasoner",
    ('deepseek', 'deepseek-chat'): 'deepseek/deepseek-chat',
    ('volcengine', 'deepseek-chat'): 'volcengine/ep-20250210170324-dd9g4',
    ('volcengine', 'deepseek-R1-0528'): 'volcengine/ep-20250612143101-qf6n8',
    ('volcengine', 'deepseek-Seed-1.6'): 'volcengine/ep-20250627140204-clmmm',
    ('volcengine', 'Doubao-Seed-1.6-flash'): 'volcengine/ep-20250627141116-z2fv4',
    ('volcengine', 'Doubao-Seed-1.6-thinking'): 'volcengine/ep-20250627141021-h4wch',
}

DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'litellm_proxy/azure/gpt-5-chat')
TOOL_SCHEMA_MODEL = os.getenv('TOOL_SCHEMA_MODEL', 'azure/gpt-4o')


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

        self._model_cache = {}  # 真正的 LiteLlm 实例缓存
        self._model_specs = {}  # model_name -> provider model string
        self._lazy_objects = {}

        azure = 'azure'
        litellm = 'litellm_proxy'
        deepseek = 'deepseek'

        # 注册模型（不初始化）
        self._register('gpt_4o_mini', (azure, 'gpt-4o-mini'))
        self._register('gpt_4o', (azure, 'gpt-4o'))

        self._register('gemini_2_0_flash', (litellm, 'gemini-2.0-flash'))
        self._register('gemini_2_5_flash', (litellm, 'gemini-2.5-flash'))
        self._register('gemini_2_5_pro', (litellm, 'gemini-2.5-pro'))

        self._register('claude_sonnet_4', (litellm, 'claude-sonnet-4'))
        self._register('deepseek_chat', (deepseek, 'deepseek-chat'))

        # GPT-5
        self._register('gpt_5', (litellm, 'gpt-5'))
        self._register('gpt_5_nano', (litellm, 'gpt-5-nano'))
        self._register('gpt_5_mini', (litellm, 'gpt-5-mini'))
        self._register('gpt_5_chat', (litellm, 'gpt-5-chat'))

        self._register('default_litellm_model', DEFAULT_MODEL)
        self._register('tool_schema_model', TOOL_SCHEMA_MODEL)

        self._initialized = True

    def _register(self, attr_name, model_key):
        self._model_specs[attr_name] = model_key

    def _get_model(self, name: str):
        if name in self._model_cache:
            return self._model_cache[name]

        # ⬇️ 延迟 import
        from google.adk.models.lite_llm import LiteLlm

        model_key = self._model_specs[name]
        model = model_key if name in ['default_litellm_model', 'tool_schema_model'] else MODEL_MAPPING.get(model_key)

        llm_kwargs = {}
        if isinstance(model, str) and model.endswith('gpt-5-chat') and 'litellm' in model:
            llm_kwargs = {'stream_options': {'include_usage': True}}

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] lazy init model_key={model_key}, model={model}, kwargs={llm_kwargs}'
        )

        instance = LiteLlm(model=model, **llm_kwargs)
        self._model_cache[name] = instance
        return instance

    def _get_opik_tracer(self):
        if 'opik_tracer' in self._lazy_objects:
            return self._lazy_objects['opik_tracer']

        from opik.integrations.adk import OpikTracer

        logger.info(
            f'[{MATMASTER_AGENT_NAME}] lazy init OpikTracer'
        )

        tracer = OpikTracer()
        self._lazy_objects['opik_tracer'] = tracer
        return tracer

    @property
    def gpt_4o_mini(self):
        return self._get_model('gpt_4o_mini')

    @property
    def gpt_4o(self):
        return self._get_model('gpt_4o')

    @property
    def gemini_2_5_flash(self):
        return self._get_model('gemini_2_5_flash')

    @property
    def gpt_5_chat(self):
        return self._get_model('gpt_5_chat')

    @property
    def gpt_5_mini(self):
        return self._get_model('gpt_5_mini')

    @property
    def gemini_2_5_pro(self):
        return self._get_model('gemini_2_5_pro')

    @property
    def deepseek_chat(self):
        return self._get_model('deepseek_chat')

    @property
    def default_litellm_model(self):
        return self._get_model('default_litellm_model')

    @property
    def tool_schema_model(self):
        return self._get_model('tool_schema_model')

    @property
    def opik_tracer(self):
        return self._get_opik_tracer()

def create_default_config() -> LLMConfig:
    return LLMConfig()


MatMasterLlmConfig = create_default_config()
