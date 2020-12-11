# ghtop
> See what's happening on GitHub in real time (also helpful if you need to use up your API quota as quickly as possible).

`ghtop` provides a number of views of all current public activity from all users across the entire GitHub platform. (Note that GitHub delays all events by five minutes.)

<img style="width:850px" width="850" src="https://user-images.githubusercontent.com/56260/101270865-3f033780-3732-11eb-8dcc-97caf7cc58e6.png">

## Install

`pip install ghtop`.

## How to use

Run `ghtop -h` to view the help. There are 4 views you can choose: `ghtop simple`, `ghtop tail`, `ghtop quad`, or `ghtop users`. Each are shown and described below.

### ghtop simple

A simple dump to your console of all events as they happen.

<img src="https://user-images.githubusercontent.com/346999/101861674-79e7df80-3b25-11eb-92d3-f888843f4aa2.png" style="width:500px" width="500">

### ghtop tail

Like `simple`, but removes most bots, and only includes releases, issues and PRs (open, close, and comment events). A summary of the frequency of push events is also shown at the bottom of the screen.

<img src="https://user-images.githubusercontent.com/346999/101861658-69376980-3b25-11eb-96ef-9d68f075abf7.png" style="width:700px" width="700">

### ghtop quad

The same information as `tail`, but in a split window showing separately PRs, issues, pushes, and releases. This view does not remove bot activity.

<img src="https://user-images.githubusercontent.com/346999/101861560-2ecdcc80-3b25-11eb-9fba-25382b2df65f.png" style="width:900px" width="900">

### ghtop users

A summary of activity for the most active current users, including bots.

<img src="https://user-images.githubusercontent.com/346999/101861612-4b6a0480-3b25-11eb-8124-19bb2434c27e.png" style="width:500px" width="500">

----

Shared under the MIT license with ♥ by @nat
