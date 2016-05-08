===========================================
async_tasks - Lightweight async build tool
===========================================
microbuild fork

Added
========

* Async executing on worker
* Time of executing of each task
* Better logging


Rewrited
========
* Logging with case thread-safe
* Task executing


Removed
========
* Arg parsing and cl interface (will add soon)
* Ignore task


Example
========

::

    import os
    import shutil
    import zipfile

    import requests

    from async_tasks.async_tasks import task, run

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
    def load_logo(logger):
        file_address = load_file("https://avatars1.githubusercontent.com/u/13404754?v=3&s=460", "punksta_logo.png")
        return file_address


    @task(create_temp_dir)
    def load_content(logger):
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


    run(clear_files, 2)

output:
::

    build started (log_result, zip_result, load_logo, load_content, create_temp_dir, clear_files)
    task log_result(load_content, load_logo) is added to queue
    task load_content(create_temp_dir) is added to queue
    task create_temp_dir is added to queue
    task create_temp_dir is started
       create_temp_dir:  clear temp dir
    task create_temp_dir is completed in 0 seconds
    task load_logo(create_temp_dir) is added to queue
    task load_logo(create_temp_dir) is started
    task load_logo(create_temp_dir) is completed in 1 seconds
    task load_content(create_temp_dir) is started
    task load_content(create_temp_dir) is completed in 1 seconds
    task zip_result(load_content, load_logo) is added to queue
    task log_result(load_content, load_logo) is started
       log_result:  ./temp/example.py loaded
       log_result:  ./temp/punksta_logo.png loaded
    task log_result(load_content, load_logo) is completed in 0 seconds
    task zip_result(load_content, load_logo) is started
       zip_result:  zip loaded files into./temp/result.zip
    task zip_result(load_content, load_logo) is completed in 0 seconds
    task clear_files(log_result, zip_result) is started
       clear_files:  clear zipped files
    task clear_files(log_result, zip_result) is completed in 0 seconds
    build ended (log_result, zip_result, load_logo, load_content, create_temp_dir, clear_files) in 2 seconds

    Process finished with exit code 0


License
=======

microbuild is licensed under a MIT license. See `LICENSE.txt`_.

.. _LICENSE.txt: https://github.com/CalumJEadie/microbuild/blob/master/LICENSE.txt
