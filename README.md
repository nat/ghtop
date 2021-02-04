# ghtop
> See what's happening on GitHub in real time (also helpful if you need to use up your API quota as quickly as possible).


`ghtop` provides a number of views of all current public activity from all users across the entire GitHub platform. (Note that GitHub delays all events by five minutes.)

<img width="650" src="https://user-images.githubusercontent.com/1483922/105071141-0c3ea580-5a39-11eb-8808-34952c0bf26d.gif" style="max-width: 650px">

## Install

Either `pip install ghtop` or `conda install -c fastai ghtop`.

## How to use

Run `ghtop -h` to view the help:

```
$ ghtop -h
usage: ghtop [-h] [--include_bots] [--types TYPES] [--pause PAUSE] [--filt {users,repo,org}] [--filtval FILTVAL] {tail,quad,users,simple}

positional arguments:
  {tail,quad,users,simple}  Operation mode to run

optional arguments:
  -h, --help                show this help message and exit
  --include_bots            Include bots (there's a lot of them!) (default: False)
  --types TYPES             Comma-separated types of event to include (e.g PushEvent) (default: )
  --pause PAUSE             Number of seconds to pause between requests to the GitHub api (default: 0.4)
  --filt {users,repo,org}   Filtering method
  --filtval FILTVAL         Value to filter by (for `repo` use format `owner/repo`)
```

There are 4 views you can choose: `ghtop simple`, `ghtop tail`, `ghtop quad`, or `ghtop users`. Each are shown and described below. All views have the following options:

- `--include_bots`: By default events that appear to be from bots are excluded. Add this flag to include them
- `--types TYPES`: Optional comma-separated list of event types to include (defaults to all types). For a full list of types, see the GitHub [event types docs](https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/github-event-types)
- `--pause PAUSE`: Number of seconds to pause between requests to the GitHub api (default: 0.4).  It is helpful to adjust this number if you want to get events more or less frequently.  For example, if you are filtering all events by an org, then you likely want to pause for a longer period of time than the default.
- `--filt` and `--filtval`: Optionally filter events to just those from one of: `user`, `repo`, or `org`, depending on `filt`. `filtval` is the value to filter by. See the [GitHub docs](https://docs.github.com/en/free-pro-team@latest/rest/reference/activity#list-public-events) for details on the public event API calls used.

**Important note**: while running, `ghtop` will make about 5 API calls per second. GitHub has a quota of 5000 calls per hour. When there are 1000 calls left, `ghtop` will show a warning on every call.

### ghtop simple

A simple dump to your console of all events as they happen.

<img src="https://user-images.githubusercontent.com/1483922/105074536-56298a80-5a3d-11eb-8e8c-32ba33e09405.png" width="650" style="max-width: 650px">

### ghtop tail

Like `simple`, but only includes releases, issues and PRs (open, close, and comment events). A summary of the frequency of different kind of events along with sparklines are shown at the top of the screen.

<img src="https://user-images.githubusercontent.com/1483922/105074448-398d5280-5a3d-11eb-9603-3def521d87e5.png" width="650" style="max-width: 650px">

### ghtop quad

The same information as `tail`, but in a split window showing separately PRs, issues, pushes, and releases.

<img src="https://user-images.githubusercontent.com/1483922/105074862-cb955b00-5a3d-11eb-99c5-3125bb98910b.png" width="650" style="max-width: 650px">

### ghtop users

A summary of activity for the most active current users.

<img src="https://user-images.githubusercontent.com/1483922/105075363-8887b780-5a3e-11eb-9f7a-627268ac465f.png" width="650" style="max-width: 650px">

----

Shared under the MIT license with ♥ by @nat
