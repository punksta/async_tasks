from distutils.core import setup

setup(
   name="async_tasks",
   version="0.4.0",
   author="Stanislav Shakirov",
   author_email="skinnystas@gmail.com",
   url="https://github.com/punksta/async_tasks",
   packages=["async_tasks"],
   license="MIT License",
   description="Lightweight async build tool",
   long_description=open("README.rst").read()+"\n"+open("CHANGES.rst").read()
)
