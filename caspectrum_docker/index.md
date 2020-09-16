# DX Spectum in Docker Containers

[DX Spectrum](https://www.broadcom.com/info/aiops/dx-spectrum) is a commercial network monitoring software by Broadcom. It was previously known as CA Spectrum.

Historically DX Spectrum has to be installed on either a Windows, Solaris or Linux server. Recently Broadcom added support for running DX Spectrum in Docker containers.
Unfortunately the product documentation is a bit sparse on the subject so here are my notes on running DX Spectrum 10.4.2 in Docker Containers under Docker-Compose.

## Step 1: Download the Docker images

As DX Spectrum is a commercial software, the Docker images are not available on the Docker Hub. One has to have an account on the Broadcom web site 
for downloading the necessary images. As of current release 10.4.2 there are several files that have to be downloaded. Each of them are a couple of GB large.

* ``CA Spectrum SpectroSERVER Docker 10.4.1.tar.gz``
* ``CA Spectrum SDC Docker 10.4.1.tar.gz``
* ``CA Spectrum OneClick Server Docker 10.4.1.tar.gz``
* ``CA SPECTRUM ONE CLICK SERVER AND SRM DOCKER 10.4.1.TAR.GZ`` (This includes ``CA Spectrum OneClick Server Docker 10.4.1.tar.gz``
* ``CA Spectrum 10.4.1 Readme.txt``
* ``CA Spectrum 10.4.1 Checksums.xlsx``

One of the utterly brain-dead things about the download process is that the actual filenames are generic like ``GEN500000000003300.tar.gz`` or 
``GEN500000000003310.tar.gz``. Whoever came up with that must have been intent on annoying their customers as much as possible. 

## Step 2: Load Docker images 

Once the files are downloaded they can be loaded into Docker. For a full installation the SpectroSERVER, SDC and combined OneClick/SRM images are needed. Make sure
that you have enough disk space for this step as the images are very big. 

```console
$ gzcat GEN500000000003300.tar | docker image load
```

## Step 3: "Installation"

When the Docker images are used first they trigger the actual installation of the individual components. This takes a while and you certainly don't want to repeat
this process over and over again whenever you start the container from scratch. Interestingly the official documentation does not mention this at all which can
cause a lot of pain later. My solution was to save the containers into new images once the installation is complete. This is shown in the examples.

### SpectroServer

### OneClick and SRM

### DC

## Step 4: Docker-Compose and supporting files

As the individual components of DX Spectrum are split into seperate Docker images/containers it makes perfect sense to create a ``docker-compose.yml`` file
to tie it all together. This also takes care of the various volumes one should create for storing data that must survive a restart (this is work in progress and 
I might have missed things here).

### docker-compose.yml

### hostrc

### spectrum.env

## Step 5: Starting DX Spectrum

Starting the Docker containers does not actually start DX Spectrum. This may be unusual but allows the user to retain some control over when to start what.
One has to "log into" the running containers and run the following commands for starting DX Spectrum. 

