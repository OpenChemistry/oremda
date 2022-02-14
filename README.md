# Open Reproducible Electron Microscopy Data Analysis (OREMDA)

The OREMDA project is developing an open source platform for the analysis and visualization of electron microcopy data sets. We are leveraging container technologies to encapsulate processing into scalable, reproducible pipelines.

<img src="https://github.com/OpenChemistry/oremda/blob/master/docs/images/peak.png?raw=true" >

The OREMDA project is funded by DOE Office of Science contract DE-SC0021601.

Packages
--------

The platform is broken up into several packages held in this monorepo.

- [oremda-core](core/) - the share library used by all packages.
- [oremda-cli](cli/) - the command line interface used interact with the platform.
- [oremda-engine](engine/) - the engine used to execution analysis pipelines.
- [oremda-server](server/) - the FastAPI application exposing the platforms RESTful API.
- [oremda-api](api/) - the API that operators are written to.
- [oremda](meta/) - a meta package that can be used to install the entire platform.

Installation
------------

The simplest way to install on the desktop is to use the meta package. A desktop
installation requires Docker as a prerequisite.

```bash
pip install oremda
```

Getting started
---------------
Fetch the OREMDA operator images by issuing the following command:

```bash
oremda pull
```



Bring up the server components by issuing the following command:

```bash
oremda start
```

Then point your browser to: http://localhost:8000

Development
-----------
To setup up a development environment the [following script](scripts/poetry/link.sh)
can be used to cross link all the dependencies between the packages so local changes
are used. Once development is finished there is a corresponding [unlink script](scripts/poetry/unlink.sh)
that can be used to unlink the local directories.

Contributing
------------

Our project uses GitHub for code review, please fork the project and make a
pull request if you would like us to consider your patch for inclusion.

![Kitware, Inc.][KitwareLogo]

  [KitwareLogo]: http://www.kitware.com/img/small_logo_over.png "Kitware"
