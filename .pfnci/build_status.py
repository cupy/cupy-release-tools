#!/usr/bin/env python

import json
import os
import re
import subprocess
import sys
import urllib.request


def _call_api(api, request, *, base='https://ci.preferred.jp/a', token=None):
    if token is None:
        token = _get_token()
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


def _get_token():
    if 'FLEXCI_TOKEN' in os.environ:
        return os.environ['FLEXCI_TOKEN']

    proc = subprocess.run(
        ['imosci', 'config', '-format', 'pbtxt'],
        capture_output=True, text=True)
    assert proc.returncode == 0, 'failed to execute imosci config command'
    for line in proc.stdout.splitlines():
        m = re.fullmatch(r'\s+uuid:\s+"(.+)"', line)
        if m is None:
            continue
        return m.group(1)
    assert False, 'FlexCI token unavailable'


def get_jobs(job_ids):
    response = _call_api('get_jobs', {
        'queries': [{'job_id': {'id': x}} for x in job_ids]
    })

    jobs = {}
    for job in response['results']:
        job_id = job['job']['job_id']['id']
        command = job['job']['config']['command']
        run_id = None
        if 'execution_run_ids' in job['job']:
            run_id = max(
                [x['id'] for x in job['job']['execution_run_ids']])
        jobs[job_id] = (command, run_id)
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

    all_ready = True
    failed = False
    for job_id in sorted(jobs.keys()):
        command, run_id = jobs[job_id]
        exit_status = stats.get(job_id, None)
        if run_id is None:
            progress = '⌛️ WAIT'
            all_ready = False
        elif exit_status is None:
            progress = '💪 BUILD'
            all_ready = False
        elif exit_status == 0:
            progress = '✅ OK'
        else:
            progress = '🚨 FAIL'
            all_ready = False
            failed = True
        print(f'Job #{job_id}: {command} ... {progress}: '
              f'https://ci.preferred.jp/r/job/{job_id} (Exec #{run_id})')

    print()
    if all_ready:
        print('Result: 🚀 Ship it!')
    elif failed:
        print('Result: 😨 Need to fix failures')
    else:
        print('Result: ☕️ Wait until all assets are ready...')


main()
