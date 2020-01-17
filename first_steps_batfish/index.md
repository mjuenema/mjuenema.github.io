# First Steps with Batfish

A few months ago I stumbled across the [Batfish network configuration analysis tool](https://www.batfish.org/). 
I watched some of the videos on the homepage and was completely amazed by what the tool seems to be capable  of. At the 
same time I was equally frustrated by how complicated even the "basic" examples appeared. It appears that on top of 
learning Batfish you also have to learn [Pandas](https://pandas.pydata.org/) in order to do anything useful. 
I am familiar with many prominent Python libraries but had never used Pandas before. Maybe I have just missed out
on something wonderful so far.

Now a few months later my motiviation for learning Batfish has not changed. I am a systems and network engineer and 
responsible for an infrastructure of almost 350 Cisco routers, switches and firewalls in addition to a number of Linux 
servers. Anyone who has ever managed more than - let's say two - devices understands that keeping configurations 
consistent across them all is a challenge. On top of this, I am yet to see an organisation that maintains a lab/test 
environment that truly matches the production environment. Batfish promises to help out...

## Preparations

The Batfish tool is provided as a [Docker container](https://hub.docker.com/r/batfish/allinone). If you are not
familiar with Docker, then unfortunately you must leave me here and come back once you are. Otherwise go ahead 
and pull the `allinone` image from the registry.

```console
$ docker pull batfish/allinone
```

One of the appealing features of Batfish is that it creates a model of your infrastructure by simply parsing all
configuration files. This sounds rather magic and I am going to put this to the test. So to get started, create a new
project directory and the directory structure Batfish expects.

```console
$ mkdir -vp My_First_Steps_with_Batfish/data/{configs,hosts,iptables}
mkdir: created directory 'My_First_Steps_with_Batfish'
mkdir: created directory 'My_First_Steps_with_Batfish/data'
mkdir: created directory 'My_First_Steps_with_Batfish/data/configs'
mkdir: created directory 'My_First_Steps_with_Batfish/data/hosts'
mkdir: created directory 'My_First_Steps_with_Batfish/data/iptables'
```

For the purpose of this article I am going to focus on the Cisco configurations. I simply copied the daily backups
we take into the `configs/` directory. You do have regular backups of your network devices, don't you???

```console
$ cd My_First_Steps_with_Batfish/
$ cp path/to/cisco/backups*.cfg data/configs/
```

## Starting Batfish

You can either start the Batfish container with lots of command line arguments or use the `docker-compose.yml` below.

### Starting Batfish container directly

```console
$ docker run --name batfish -v batfish-data:/data -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone
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
      - "./data:/data"
      ports:
      - 8888:8888
      - 9996:9996
      - 9997:9997
```

```console
$ docker-compose up
```

## The Jupyter interface

```
...

```

When you open the URL that Batfish prints on the screen in a browser you will be presented with a Jupyter
