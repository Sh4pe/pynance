[![Build Status](https://travis-ci.org/Sh4pe/pynance.svg?branch=master)](https://travis-ci.org/Sh4pe/pynance)
[![Build status](https://ci.appveyor.com/api/projects/status/f63tmsr561j9pq39?svg=true)](https://ci.appveyor.com/project/Sh4pe/pynance)
[![codecov](https://codecov.io/gh/Sh4pe/pynance/branch/master/graph/badge.svg)](https://codecov.io/gh/Sh4pe/pynance)

# Prerequisites

* [doit](http://pydoit.org) - install `doit`

# Common tasks

Run the tests.

```
$> doit test
```

Start Jupyter notebook.

```
$> doit notebook
```

## Dash app
Make sure you have the following packages installed
* dash
* dash_core_components
* dash_html_component

To start and show in webbrowser, type

```
$> doit dash_app
```