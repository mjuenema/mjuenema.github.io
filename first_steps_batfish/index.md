# First Steps with Batfish

>> This article is currently work-in-progress!

A few months ago I stumbled across the [Batfish network configuration analysis tool](https://www.batfish.org/). 
I watched some of the videos on the homepage and was completely amazed by what the tool seems to be capable  of. At the 
same time I was equally frustrated by how complicated even the "basic" examples appeared. It seems that on top of 
learning Batfish one also has to learn [Pandas](https://pandas.pydata.org/) in order to do anything useful. 
I am familiar with many prominent Python libraries but had never used Pandas before. Maybe I have just missed out
on something wonderful so far.

Now a few months later my motiviation for learning Batfish has not changed. I am a systems and network engineer and 
responsible for an infrastructure of almost 350 Cisco routers, switches and firewalls in addition to a number of Linux 
servers. Anyone who has ever managed more than - let's say two - devices understands that keeping configurations 
consistent across them all is a challenge. On top of this, I am yet to see an organisation that maintains a lab/test 
environment that truly matches the production environment. Batfish promises to help out...

## Architecture

This one really caught me out at the beginning. Many articles about Batfish use just the examples that are included in
the [Docker `batfish/allinone` container](https://hub.docker.com/r/batfish/allinone) and *not* any real network
configurations. 
If you wanted to analyse your *own* network configurations you could use the leaner
[Docker `batfish/batfish` container](https://hub.docker.com/r/batfish/batfish) instead. The third option is to use the 
[Docker `batfish/allinone` container](https://hub.docker.com/r/batfish/allinone), ignore the examples and include your
*own* network configurations.

I like to distinguish three different components to a "Batfish architecure": the Batfish service, Batfish applications 
and network configurations.

* The Batfish service runs inside a Docker container (`batfish/allinone` or `batfish/batfish`). The service uses 
  a Docker volume mounted as `/data` for its own internal purposes. This is *not* where the network configurations
  that are meant to be analysed are located.
* Batfish applications can be written using the 
  [PyBatfish Python bindings](https://pybatfish.readthedocs.io/en/latest/index.html).
  Batfish applications connect to TCP ports the Docker container exposes to interact (upload configurations and run queries) 
  with the Batfish service. 
  * The `batfish/allinone` container already contains the PyBatfish bindings so the example applications can run 
    from within the container. In fact the `batfish/allinone` will start a [Jupyter](https://jupyter.org/) interface
    for convenience.
  * The `batfish/batfish` container is meant to be used by applications from outside the container, 
    e.g. a Python virtual environment on the host.
* A Batfish applications must upload network configurations to the Batfish service before it can analyse them.
  * The `batfish/allinone` container includes example configurations ready for anlaysis. 
  * The `batfish/batfish` container does not include the example configurations. The user must collect them
    into a specific directory structure and program the Batfish application to upload them to the Batfish service.
  * It is possible to use your own network configurations with the `batfish/allinone` container, ignoring the
    built-in examples while still using the Jupyter Notebook, and this is what I am going to do in this article. 

## Preparations

The Batfish tool is provided as a [Docker container](https://hub.docker.com/r/batfish/allinone). If you are not
familiar with Docker, then unfortunately you must leave me here and come back once you are. 

As mentioned in the previous section I am going to use the `batfish/allinone` container but with my own network configurations. Go ahead and pull the `batfish/allinone` image from the registry. 

```console
$ docker pull batfish/allinone
```

One of the appealing features of Batfish is that it creates a model of your infrastructure by simply parsing all
configuration files. This sounds rather magic and I am going to put this to the test. So to get started, create a new
project directory and the directory structure as shown below. I am going to mount the `input/` folder into the
`batfish/allinone` container later so I can use my own network configurations instead of the examples included
in the `batfish/allinone` container. You could choose a different name than `input/`, but must keep the
names of the three sub-directories.

```console
$ mkdir -vp My_First_Steps_with_Batfish/input/{configs,hosts,iptables}
mkdir: created directory 'My_First_Steps_with_Batfish'
mkdir: created directory 'My_First_Steps_with_Batfish/input'
mkdir: created directory 'My_First_Steps_with_Batfish/input/configs'
mkdir: created directory 'My_First_Steps_with_Batfish/input/hosts'
mkdir: created directory 'My_First_Steps_with_Batfish/input/iptables'
```

For the purpose of this article I am going to focus on the Cisco configurations. I simply copied the daily backups
we take into the `configs/` directory. `input/hosts` and `input/iptables` remain unused.
```console
$ cd My_First_Steps_with_Batfish/
$ cp path/to/cisco/backups*.cfg input/configs/
```

## Starting Batfish

You can either start the Batfish container with lots of command line arguments or use the `docker-compose.yml` below.
Note how I make my own configurations available to the container by mounting the `input/` directory read-only as `/input`.
The `/data` volume is used by the Batfish service internally.

### Starting Batfish container directly

```console
$ docker run --name batfish -v batfish-data:/data -v ./input:/input:ro \
             -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone
```

### Starting Batfish container with docker-compose

```yaml
---
# docker-compose.yml for Batfish
version: '3'
services:
    batfish:
      image: batfish/allinone
      volumes:
      - "./input:/input"
      - batfish-data:/data"
      ports:
      - 8888:8888
      - 9996:9996
      - 9997:9997
      
volumes:
  batfish-data:
```

```console
$ docker-compose up
```

## The Jupyter interface

The `batfish/allinone` Batfish container includes [Jupyter](https://jupyter.org/) for experimenting with
the [Batfish Python bindings](https://pybatfish.readthedocs.io/en/latest/index.html). 

```
Recreating my_first_steps_with_batfish_batfish_1_e8b2f84fc410 ... done
Attaching to my_first_steps_with_batfish_batfish_1_e8b2f84fc410
batfish_1_e8b2f84fc410 | [I 07:48:12.156 NotebookApp] Writing notebook server cookie secret to /data/.local/share/jupyter/runtime/notebook_cookie_secret
batfish_1_e8b2f84fc410 | [I 07:48:13.457 NotebookApp] Serving notebooks from local directory: /notebooks
batfish_1_e8b2f84fc410 | [I 07:48:13.457 NotebookApp] The Jupyter Notebook is running at:
batfish_1_e8b2f84fc410 | [I 07:48:13.462 NotebookApp] http://afc12963c0a5:8888/?token=aee2f45fae4c3b2153277cc874f8d58ca8eac713bc5b6610
batfish_1_e8b2f84fc410 | [I 07:48:13.462 NotebookApp]  or http://127.0.0.1:8888/?token=aee2f45fae4c3b2153277cc874f8d58ca8eac713bc5b6610
batfish_1_e8b2f84fc410 | [I 07:48:13.462 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
batfish_1_e8b2f84fc410 | [W 07:48:13.478 NotebookApp] No web browser found: could not locate runnable browser.
batfish_1_e8b2f84fc410 | [C 07:48:13.479 NotebookApp] 
batfish_1_e8b2f84fc410 |     
batfish_1_e8b2f84fc410 |     To access the notebook, open this file in a browser:
batfish_1_e8b2f84fc410 |         file:///data/.local/share/jupyter/runtime/nbserver-7-open.html
batfish_1_e8b2f84fc410 |     Or copy and paste one of these URLs:
batfish_1_e8b2f84fc410 |         http://afc12963c0a5:8888/?token=aee2f45fae4c3b2153277cc874f8d58ca8eac713bc5b6610
batfish_1_e8b2f84fc410 |      or http://127.0.0.1:8888/?token=aee2f45fae4c3b2153277cc874f8d58ca8eac713bc5b6610
```

Copy the URL into your browser and you will be presented with a list of example Jupyter Notebooks. These I am
going to ignore completely for the purpose of this article as they are covered by many other tutorials. 
The `startup.py` script at the end of the directory listing conveniently imports many PyBatfish modules. 
It also contains a nice formatter for Pandas Data Frames so we are going to use it in a moment. It is not normally
required.

This article continues in the [Jupyter Notebook](first_steps_batfish.xyz).




