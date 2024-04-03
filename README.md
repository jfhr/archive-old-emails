# archive-old-emails

Python script that connects to an IMAP server and automatically archives old, unimportant emails.

More specifically:

- Looks for a mailbox called "Archive" or "Archived"
- SEARCH the INBOX for messages with an internal date BEFORE 7 days ago and without the \Flagged flag
    - Because the BEFORE parameter doesn't support a time or timezone, only the date is passed. This will only select emails with an internal date before the last midnight before or equal to 7 days before the current UTC time.
- COPY the messages to the Archive box, set the \Deleted flag on them from the INBOX and EXPUNGE the INBOX

## Usage

The script must be provided with IMAP connection details, specifically host, port, username, password.
Each value can be provided either on the command line or in an environment variable.

```
usage: main.py [-h] [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD]

options:
  -h, --help           show this help message and exit
  --host HOST          IMAP server host. Default: $IMAP_HOST
  --port PORT          IMAP server port. Default: $IMAP_PORT
  --username USERNAME  IMAP username. Default: $IMAP_USERNAME
  --password PASSWORD  IMAP password. Default: $IMAP_PASSWORD
```

## Prerequisites

The script was tested on Python 3.12.2. As far as I can tell it should work on version 3.5 and up.

## Test

A few doctests are included. Run:

```
python -m doctest ./main.py
```

If there is no output (and the exit code is 0), everything worked. 

Alternatively, run

```
python -m doctest -v ./main.py
```

for verbose output (also prints succesful tests).

## License

This is licensed under <a href="http://creativecommons.org/publicdomain/zero/1.0" target="_blank" rel="license noopener noreferrer">CC0 1.0</a>.

## Further reading

- [IMAP specification: RFC 3501](https://datatracker.ietf.org/doc/html/rfc3501.html)
- [python documentation: imaplib](https://docs.python.org/3/library/imaplib.html)
- [python documentation: doctest](https://docs.python.org/3/library/doctest.html)
