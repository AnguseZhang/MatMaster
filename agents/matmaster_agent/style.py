from toolsy.i8n import I18N


def get_job_complete_card(i18n: I18N, job_id):
    return f"""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    color: white;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <div style="
            background: rgba(255, 255, 255, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            font-size: 12px;
            font-weight: bold;
        ">🚀 {i18n.t("JobStatus")}</div>
        <div style="
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
        ">{i18n.t("Job")}ID：{job_id}</div>
    </div>
    <div style="
        font-size: 16px;
        font-weight: 500;
        margin-top: 8px;
    ">✅ {i18n.t("JobCompleted")}</div>
    <div style="
        font-size: 14px;
        opacity: 0.9;
        margin-top: 6px;
    ">{i18n.t("ResultRetrieving")}...</div>
</div>
"""


def hallucination_card(i18n: I18N):
    def _inner_css():
        return """
    <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        @keyframes progress {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(250%); }
        }
    </style>
</div>
"""

    return (
        f"""
<div style="
    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    max-width: 500px;
    width: 100%;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin: 20px auto;
">
    <div style="
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
    ">
        <div style="
            font-size: 28px;
            margin-right: 16px;
            animation: pulse 2s infinite;
        ">🔄</div>
        <div style="flex: 1;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 4px;
            ">{i18n.t("JobSubmitHallucination")}</div>
            <div style="
                font-size: 14px;
                opacity: 0.9;
            ">{i18n.t("JobSubmitHallucinationAction")}</div>
        </div>
    </div>
    <div style="
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 2px;
        margin-top: 16px;
        overflow: hidden;
    ">
        <div style="
            height: 100%;
            width: 60%;
            background: white;
            border-radius: 2px;
            animation: progress 2s ease-in-out infinite;
        "></div>
    </div>"""
        + _inner_css()
    )
