#!/usr/bin/env python

import json
import os
import sys
import urllib.request


def _call_api(api, request, *, base='https://ci.preferred.jp/a', token=None):
    if token is None:
        token = os.environ['FLEXCI_TOKEN']
    req = urllib.request.Request(
        f'{base}/{api}',
        data=json.dumps({'request': request}).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Cookie': f'csrf=api; token={token}',
            'X-CSRF-Token': 'api',
        }
    )
    with urllib.request.urlopen(req) as res:
        response = json.loads(res.read())
    if response['response'] is None:
        raise RuntimeError(response)
    return response['response']


def get_jobs(job_ids):
    response = _call_api('get_jobs', {
        'queries': [{'job_id': {'id': x}} for x in job_ids]
    })

    jobs = {}
    for job in response['results']:
        job_id = job['job']['job_id']['id']
        command = job['job']['config']['command']
        exec_run_id = None
        if 'execution_run_ids' in job['job']:
            exec_run_id = max(
                [x['id'] for x in job['job']['execution_run_ids']])
        jobs[job_id] = (command, exec_run_id)
    return jobs


def get_job_run_stats(jobs):
    run_ids = [x[1] for x in jobs.values() if x[1] is not None]
    if len(run_ids) == 0:
        # None of the job started.
        return {}
    response = _call_api('get_runs', {
        'queries': [{'run_id': {'id': x}} for x in run_ids]
    })
    stats = {}
    for run in response['results']:
        job_id = run['run']['job_id']['id']
        exit_status = None
        if 'end_timestamp' in run['run']:
            exit_status = run['run'].get('exit_status', 0)
        stats[job_id] = exit_status
    return stats


def main():
    job_ids = [int(x) for x in sys.argv[1:]]
    jobs = get_jobs(job_ids)
    stats = get_job_run_stats(jobs)

    for job_id in sorted(jobs.keys()):
        command, exec_id = jobs[job_id]
        exit_status = stats.get(job_id, None)
        if exec_id is None:
            progress = '⌛️ WAIT'
        elif exit_status is None:
            progress = '💪 BUILD'
        elif exit_status == 0:
            progress = '✅ OK'
        else:
            progress = '🚨 FAIL'
        print(f'Job #{job_id}: {command} ... {progress}: '
              f'https://ci.preferred.jp/r/job/{job_id} (Exec #{exec_id})')


main()
