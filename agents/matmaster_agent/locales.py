from toolsy.i8n import I18N

translations = {
    'en': {
        'JobStatus': 'Job Status',
        'Job': 'Job',
        'JobCompleted': 'Job Completed',
        'ResultRetrieving': 'Result Retrieving',
        'JobSubmitHallucination': 'Job Submit Hallucination',
        'JobSubmitHallucinationAction': 'Detected a task submission hallucination, I will retry the submission with the same parameters.',
        'ToolInvocateHallucination': 'Tool Invocate Hallucination',
        'ToolInvocateHallucinationAction': 'Detected a task submission hallucination, I will retry the tool call with the same parameters.',
        'ToolInvocateHallucinationRetryFailed': 'Tool call retry failed. Please try again manually later.',
        'ToolResponseFailed': 'Tool call failed.',
    },
    'zh': {
        'JobStatus': '任务状态',
        'Job': '任务',
        'JobCompleted': '任务已完成',
        'ResultRetrieving': '结果获取中',
        'JobSubmitHallucination': '任务提交幻觉',
        'JobSubmitHallucinationAction': '检测到任务提交幻觉，我将使用相同参数重试提交。',
        'ToolInvocateHallucination': '工具调用幻觉',
        'ToolInvocateHallucinationAction': '检测到工具调用幻觉，我将使用相同参数重试工具调用。',
        'ToolInvocateHallucinationRetryFailed': '工具调用重试失败，请稍后手动重试',
        'ToolResponseFailed': '工具调用失败',
    },
}

i18n = I18N(translations=translations)
