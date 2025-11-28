def step_card(index, i18n):
    return f"""
<div style="
    background-color: #f0f8ff;
    border: 1px solid #d4e3fc;
    border-left: 4px solid #1890ff;
    border-radius: 4px;
    padding: 6px 10px;
    margin: 4px 0;
    font-family: sans-serif;
    color: #096dd9;
    line-height: 1.3;
    display: inline-block;
">
  <strong>{i18n.t('Step')} {index}</strong>
</div>
"""


def all_summary_card(i18n):
    return f"""
<div style="
    background-color: #f0f9eb;
    border: 1px solid #e1f3d8;
    border-left: 4px solid #67c23a;
    border-radius: 4px;
    padding: 6px 10px;
    margin: 4px 0;
    font-family: sans-serif;
    color: #529b2e;
    line-height: 1.3;
    display: inline-block;
">
  <strong>{i18n.t('PlanSummary')}</strong>
</div>
"""


def parameters_ask_confirm_card():
    return """
<div style="
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-left: 4px solid #ff9800;
  border-radius: 4px;
  padding: 12px 16px;
  margin: 12px 0;
  font-family: sans-serif;
  color: #856404;
  line-height: 1.4;
">
  <strong>请确认上述参数是否正确？确认后将生成参数 JSON 文件。</strong>
</div>
"""
