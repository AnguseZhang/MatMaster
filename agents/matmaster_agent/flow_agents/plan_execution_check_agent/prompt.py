PLAN_EXECUTION_CHECK_INSTRUCTION = """
Summarize the executed plan and directly state the next action using imperative statements only.
If the recent plan involved parameter confirmation, display those parameters to the user.
If the recent plan involved submitting a task, instruct the user to monitor the task status themselves
and specify what step to take after the task is completed.
"""
