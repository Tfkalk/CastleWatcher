# CastleWatcher
CLI to track Smithsonian exhibits

## Prerequisites

You must have Python3 installed on your computer. For macOS, you can use the system built-in
`python3` and `pip3`.

Install the necessary libraries: `pip install playwright playwright-stealth beautifulsoup4`

To use the notifications capability, ensure you have [Ntfy]'s app downloaded to your smartphone.

## Basic Usage

### Soon
Looking to visit the Smithsonian soon? Use `python3 castle.py soon`, it'll tell you any exhibits opening or closing that week.

Use the `-d`/`--days` flag to specify a different number of days, in case you're only visiting that weekend or looking to plan for the month.

### Newly Announced
`python3 castle.py upcoming` looks for newly announced, upcoming exhibits. It keeps track of the ones you have already found out about on previous
runs so it won't tell you about them again.

**Note** On your first run, it will alert you to all upcoming exhibits for a given museum.

## Take it Further: Automated with Notifications

### Schedule the Script
**TODO**

### Notifications
In the Ntfy app, add a new subscribed topic. For a free account, anyone can send any message to your topic
so do something unique that others won't think to use.

Once you have your topic set up, run `python3 castle.py configure` to set your topic name (you don't need to include the
ntfy.sh URL).

Now, any time you run `soon` or `upcoming`, you will get push alerts for closing/starting exhibits as well as any newly announced upcoming exhibits.