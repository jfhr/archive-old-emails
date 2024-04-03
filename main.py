import argparse
import datetime
import imaplib
import os
import time


def get_imap_configuration():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='IMAP server host. Default: $IMAP_HOST', default=os.environ.get('IMAP_HOST'))
    parser.add_argument('--port', help='IMAP server port. Default: $IMAP_PORT', type=int, default=os.environ.get('IMAP_PORT'))
    parser.add_argument('--username', help='IMAP username. Default: $IMAP_USERNAME', default=os.environ.get('IMAP_USERNAME'))
    parser.add_argument('--password', help='IMAP password. Default: $IMAP_PASSWORD', default=os.environ.get('IMAP_PASSWORD'))
    args = parser.parse_args()
    if not all([args.host, args.port, args.username, args.password]):
        parser.error('Missing required arguments')
    return args


def create_message_set(message_numbers):
    """
    Create a message set from a list of message numbers. The message numbers are expected to be in a list of strings.
    
    >>> create_message_set(['1', '2', '3', '5', '6', '7', '9', '10'])
    '1:3,5:7,9:10'
    >>> create_message_set(['1', '2', '3', '5', '6', '7', '9', '10', '12'])
    '1:3,5:7,9:10,12'
    >>> create_message_set(['2', '3', '5', '7', '11'])
    '2:3,5,7,11'
    >>> create_message_set([])
    ''
    """
    range_tuples = []
    current_range_start = None
    current_range_end = None
    for no in map(int, message_numbers):
        if current_range_start is None:
            current_range_start = no
            current_range_end = no
        elif no == current_range_end + 1:
            current_range_end = no
        else:
            range_tuples.append((current_range_start, current_range_end))
            current_range_start = no
            current_range_end = no
    if current_range_start is not None:
        range_tuples.append((current_range_start, current_range_end))
        
    message_ranges = []
    for start, end in range_tuples:
        if start == end:
            message_ranges.append(str(start))
        else:
            message_ranges.append(f'{start}:{end}')
    
    return ','.join(message_ranges)


def find_archive_mailbox(mailboxes):
    """
    Find an archive mailbox from a list of mailboxes.

    >>> find_archive_mailbox([b'(\\\\HasNoChildren) "/" "INBOX"', b'(\\\\HasNoChildren) "/" "Archive"', b'(\\\\HasNoChildren) "/" "Archived"'])
    'Archive'
    >>> find_archive_mailbox([b'(\\\\HasNoChildren) "/" "INBOX"', b'(\\\\HasNoChildren) "/" "Archived"', b'(\\\\HasNoChildren) "/" "Trash"'])
    'Archived'
    >>> find_archive_mailbox([b'(\\\\HasNoChildren) "/" "INBOX"', b'(\\\\HasNoChildren) "/" "Trash"', b'(\\\\HasNoChildren) "/" "Spam"'])
    """
    for mailbox in mailboxes:
        mailbox = mailbox.decode().split(' "/" ')[1].strip('"')
        if mailbox.lower() == 'archive' or mailbox.lower() == 'archived':
            return mailbox
    return None


def archive_old_emails(host, port, username, password):
    # - connect to an IMAP server
    # - find a mailbox with the name "Archive" or "Archived", throw an error if no such mailbox exists
    # - open the INBOX
    # - fetch all emails
    # - filter all emails that are more than 7 days old and not flagged
    # - move those emails to the archive box
    # - log the number of emails moved

    with imaplib.IMAP4_SSL(host, port) as connection:
        connection.login(username, password)

        # Find the archive mailbox
        _, mailboxes = connection.list('""', "%")
        archive_mailbox = find_archive_mailbox(mailboxes)

        if not archive_mailbox:
            raise RuntimeError('No archive mailbox found. Please create an "Archive" or "Archived" mailbox.')

        connection.select('INBOX')

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        seven_days_ago = now_utc - datetime.timedelta(days=7)
        imap_before_date = imaplib.Time2Internaldate(seven_days_ago).split()[0] + '"'

        # SEARCH messages that are unflagged and older than 7 days
        _, message_numbers = connection.search(None, f'(BEFORE {imap_before_date} UNFLAGGED)')

        # Move messages to the archive mailbox
        message_set = create_message_set(message_numbers[0].split())

        if not message_set:
            print('No emails to archive')
            return

        connection.copy(message_set, archive_mailbox)
        connection.store(message_set, '+FLAGS', '\\Deleted')

        _, expunged = connection.expunge()
        expunged_count = len(expunged[0].split())
        print(f'{expunged_count} emails moved to {archive_mailbox}')


if __name__ == '__main__':
    configuration = get_imap_configuration()
    archive_old_emails(
        configuration.host,
        configuration.port,
        configuration.username, 
        configuration.password,
    )
