import pytest
import subprocess
import os


def test_set_int():
    key = '/test/hoge'
    value = 1
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value={2}'.format(os.environ['USER'], key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'dconf', 'read', key
    ]).strip()
    assert output == str(value)


def test_set_str():
    key = '/test/hoge'
    value = 'piyo'
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value={2}'.format(os.environ['USER'], key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'dconf', 'read', key
    ]).strip()
    assert output == "'{0}'".format(value)


def test_set_list_str():
    key = '/test/hoge'
    value = "['piyo', 'fuga']"
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value="{2}"'.format(os.environ['USER'], key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'dconf', 'read', key
    ]).strip()
    assert output == value


def test_set_list_int():
    key = '/test/hoge'
    value = "[1, 2, 3]"
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value="{2}"'.format(os.environ['USER'], key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    output = subprocess.check_output([
        'dconf', 'read', key
    ]).strip()
    assert output == value


def test_append_list_str():
    key = '/test/hoge'
    value = "['piyo', 'fuga']"
    added = 'moge'
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value="{2}"'.format(os.environ['USER'], key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value={2} state=append'.format(os.environ['USER'], key, added),
        '-i', 'localhost,',
        '-c', 'local'
    ])

    assert status == 0
    output = subprocess.check_output([
        'dconf', 'read', key
    ]).strip()
    assert output == "['piyo', 'fuga', 'moge']"


def test_remove_list_str():
    key = '/test/hoge'
    value = "['piyo', 'fuga']"
    removed = 'fuga'
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value="{2}"'.format(os.environ['USER'], key, value),
        '-i', 'localhost,',
        '-c', 'local'
    ])
    assert status == 0
    status = subprocess.check_call([
        'ansible', 'localhost', '-m', 'dconf',
        '-a', 'user={0} key={1} value={2} state=absent'.format(os.environ['USER'], key, removed),
        '-i', 'localhost,',
        '-c', 'local'
    ])

    assert status == 0
    output = subprocess.check_output([
        'dconf', 'read', key
    ]).strip()
    assert output == "['piyo']"
