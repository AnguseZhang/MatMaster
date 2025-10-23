from toolsy.i8n import I18N

translations = {
    'en': {
        'JobStatus': 'Job Status',
        'Job': 'Job',
        'JobCompleted': 'Job Completed',
        'ResultRetrieving': 'Result Retrieving',
        'JobSubmitHallucination': 'Job Submit Hallucination',
        'JobSubmitHallucinationAction': 'Detected a task submission hallucination, I will retry the submission with the same parameters.',
    },
    'zh': {
        'JobStatus': '任务状态',
        'Job': '任务',
        'JobCompleted': '任务已完成',
        'ResultRetrieving': '结果获取中',
        'JobSubmitHallucination': '任务提交幻觉',
        'JobSubmitHallucinationAction': '检测到任务提交幻觉，我将使用相同参数重试提交。',
    },
}

i18n = I18N(translations=translations)
