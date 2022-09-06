These files can be used to start Covalent using ![OpenRC](https://wiki.gentoo.org/wiki/OpenRC). Simply place the corresponding files in the correct locations for your system's init files (typically `/etc/init.d` and `/etc/conf.d`) and then add the service to the default runlevel:

```
rc-update add covalent default
```

Start the service immediately using the following:

```
rc-service covalent start
```

To view system logs, look in `/var/log/covalentd.log`.

There are a few modifications the client needs in order to interact with the Covalent service. Any user will also need to have Covalent installed at the user level, e.g., in a virtualenv or in a Conda environment. The user will need to then export the following environment variables, in correspondence with the values set in `/etc/conf.d/covalent`:

```
export COVALENT_SVC_PORT=48080
export COVALENT_DATABASE=/var/lib/covalent/dispatch.sqlite
```

At this point workflows may be submitted to the Covalent service.

To stop the service, simply run

```
rc-service covalent stop
```
