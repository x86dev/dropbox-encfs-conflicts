dropbox_encfs_conflicts
=======================

Script for resolving synchronization conflicts of EncFS-encrypted files within a Dropbox folder.

Dropbox provides file / content synchronization between multiple devices in a quite convenient
way. Due to lacking end-to-end encryption security one can create an EncFS volume within a certain
folder which then gets synchronized with Dropbox. This enables you to store more confident data
on your Dropbox account without losing the conveniece of the Dropbox ecosystem.

Using EncFS with Dropbox works with Windows (using an EncFS port), Linux (using FUSE) and even on
Android phone for mobile access (using Cryptonite or CloudFetch).

However, there is a glitch: What if you just changed the same file(s) on different devices at the
same time within your EncFS volume? Since EncFS also encrypts the file names within that volume,
Dropbox automatically renames those conflicts. This unfortunately results in either old / outdated
files and not seeing the conflicted files in your EncFS volume.

This is what this script is for: It tries to resolve the conflicted files marked by Dropbox and
re-integrates them into your EncFS volume without losing any files.

Tested on Windows only at the moment. At the time of writing this only is a plain Python script and
does not offer any fancy user interface.

Comments and ideas welcome!

If you want to say "Thank you" for providing this script, I'd appreciate using my referal link
http://db.tt/q9XZ2ylP when creating a new Dropbox account. Cheers!

