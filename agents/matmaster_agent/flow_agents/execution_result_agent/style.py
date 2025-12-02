def get_execution_result_card(text):
    return f"""
<div style="
  white-space: pre-line;
  border: 1px solid #e5e7eb;
  border-left: 6px solid #3b82f6;
  background: #eef6ff;
  color: #1e3a8a;
  padding: 14px 16px;
  margin: 16px 0;
  border-radius: 8px;
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto';
">{text}
</div>
"""
