import os
import shutil
import zipfile

import requests

from async_tasks.async_tasks import task, run, TeamCityLogger

dir = './temp/'


def load_file(url, name):
    response = requests.get(url, stream=True)
    with open(dir + name, "wb") as handle:
        handle.write(response.content)
    return dir + name


@task()
def create_temp_dir(logger):
    if not os.path.exists(dir):
        logger("create temp dir")
        os.makedirs(dir)
    else:
        logger("clear temp dir")
        shutil.rmtree(dir)
        os.makedirs(dir)


@task(create_temp_dir)
def load_logo():
    file_address = load_file("https://avatars1.githubusercontent.com/u/13404754?v=3&s=460", "punksta_logo.png")
    return file_address


@task(create_temp_dir)
def load_content():
    file_address = load_file("https://raw.githubusercontent.com/punksta/async_tasks/master/example.py", "example.py")
    return file_address


@task(load_content, load_logo)
def log_result(logger):
    for name in [load_content.result, load_logo.result]:
        logger(name + " loaded")


@task(load_content, load_logo)
def zip_result(logger):
    zf = zipfile.ZipFile(dir + 'result.zip', mode='w')

    logger("zip loaded files into" + dir + 'result.zip')

    try:
        zf.write(load_content.result)
        zf.write(load_logo.result)
    finally:
        zf.close()
    zipped = [load_content.result, load_logo.result]
    return zipped


@task(log_result, zip_result)
def clear_files(logger):
    logger('clear zipped files')

    for file in zip_result.result:
        os.remove(file)
    pass


run(clear_files, 2, TeamCityLogger())