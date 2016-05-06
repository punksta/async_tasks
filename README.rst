===========================================
async_tasks - microbuild async fork, working on concurrent.futures
===========================================
worked on python 3

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

    @task()
    def a(logger):
        logger("sleep 1 sec")
        time.sleep(1)
        pass
    
    
    @task()
    def b(logger):
        logger("sleep 2 sec")
        time.sleep(2)
        pass
    
    
    @task()
    def c(logger):
        logger("pass")
        pass
    
    
    @task(a, b, c)
    def d(logger):
        time.sleep(2)
        logger("sleep 1 sec")
        pass
    
    
    run(d, workers=3, logger=Logger())

output:

    build started (c, a, b, d)
    task a is added to queue
    task b is added to queue
    task c is added to queue
    task c is started
       c:  pass
    task c is completed in 0 seconds
    task a is started
       a:  sleep 1 sec
    task a is completed in 1 seconds
    task b is started
       b:  sleep 2 sec
    task b is completed in 2 seconds
    task d(a, b, c) is started
       d:  sleep 1 sec
    task d(a, b, c) is completed in 2 seconds
    build ended (c, a, b, d) in 4 seconds 

License
=======

microbuild is licensed under a MIT license. See `LICENSE.txt`_.

.. _LICENSE.txt: https://github.com/CalumJEadie/microbuild/blob/master/LICENSE.txt
