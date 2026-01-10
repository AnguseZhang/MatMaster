from agents.matmaster_agent.model import BohrJobInfo, JobStatus


def mapping_status(status):
    return {
        -1: 'Failed',
        -2: 'Deleted',
        0: 'Pending',
        1: 'Running',
        2: 'Finished',
        3: 'Scheduling',
        4: 'Stopping',
        5: 'Stopped',
        6: 'Terminating',
        7: 'Killing',
        8: 'Uploading',
        9: 'Wait',
    }.get(status, 'Unknown')


def has_job_running(jobs_dict: BohrJobInfo) -> bool:
    """检查是否有任何作业处于运行状态"""
    return any(job['job_status'] == JobStatus.Running for job in jobs_dict.values())


def get_running_jobs_detail(jobs_dict: BohrJobInfo):
    return [
        (job['origin_job_id'], job['job_id'], job['agent_name'])
        for job in jobs_dict.values()
        if job['job_status'] == JobStatus.Running
    ]
