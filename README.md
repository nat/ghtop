# ghtop
> See what's happening on GitHub in real time (also helpful if you need to use up your API quota as quickly as possible).


`ghtop` provides a number of views of all current public activity from all users across the entire GitHub platform. (Note that GitHub delays all events by five minutes.)

<img width="850" src="https://user-images.githubusercontent.com/56260/101270865-3f033780-3732-11eb-8dcc-97caf7cc58e6.png" style="max-width: 850px">

## Install

Either `pip install ghtop` or `conda install -c fastai ghtop`.

## How to use

Run `ghtop -h` to view the help:

```bash
$ ghtop -h
usage: ghtop [-h] [--include_bots] [--types TYPES] [--filt {user,repo,org}] [--filtval FILTVAL]
             {tail,quad,users,simple}

positional arguments:
  {tail,quad,users,simple}  Operation mode to run

optional arguments:
  -h, --help                show this help message and exit
  --include_bots            Include bots (there is a lot of them!) (default: False)
  --types TYPES             Comma-separated types of event to include (e.g PushEvent)
  --filt {user,repo,org}    Filtering method
  --filtval FILTVAL         Value to filter by (for `repo` use format `owner/repo`)
```

There are 4 views you can choose: `ghtop simple`, `ghtop tail`, `ghtop quad`, or `ghtop users`. Each are shown and described below. All views have the following options:

- `--include_bots`: By default events that appear to be from bots are excluded. Add this flag to include them
- `--types TYPES`: Optional comma-separated list of event types to include (defaults to all types). For a full list of types, see the GitHub [event types docs](https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/github-event-types)
- `--filt` and `--filtval`: Optionally filter events to just those from one of: `user`, `repo`, or `org`, depending on `filt`. `filtval` is the value to filter by. See the [GitHub docs](https://docs.github.com/en/free-pro-team@latest/rest/reference/activity#list-public-events) for details on the public event API calls used.

**Important note**: while running, `ghtop` will make about 5 API calls per second. GitHub has a quota of 5000 calls per hour. When there are 1000 calls left, `ghtop` will show a warning on every call.

### ghtop simple

A simple dump to your console of all events as they happen.

<img src="https://user-images.githubusercontent.com/346999/101861674-79e7df80-3b25-11eb-92d3-f888843f4aa2.png" width="500" style="max-width: 500px">

### ghtop tail

Like `simple`, but removes most bots, and only includes releases, issues and PRs (open, close, and comment events). A summary of the frequency of push events is also shown at the bottom of the screen.

<img src="https://user-images.githubusercontent.com/346999/101861658-69376980-3b25-11eb-96ef-9d68f075abf7.png" width="700" style="max-width: 700px">

### ghtop quad

The same information as `tail`, but in a split window showing separately PRs, issues, pushes, and releases. This view does not remove bot activity.

<img src="https://user-images.githubusercontent.com/346999/101861560-2ecdcc80-3b25-11eb-9fba-25382b2df65f.png" width="900" style="max-width: 900px">

### ghtop users

A summary of activity for the most active current users.

<img src="https://user-images.githubusercontent.com/346999/101861612-4b6a0480-3b25-11eb-8124-19bb2434c27e.png" width="500" style="max-width: 500px">

----

Shared under the MIT license with ♥ by @nat
