Agitate - A git based CMS frontend for any RESTful backend
===========================================
Author: Michael Bironneau (@MikeBrno, github: /mikebrno)

Introduction
-------------
Agitate combines the power and version control of GIT with the flexibility of RESTful APIs. It allows you to manage content for any website that has a RESTful backend and push those changes to a git repo with a git-like interface. You create a GIT repo for your content and use agitate instead of GIT to `add, commit, diff`, or any other GIT command you can think of. Agitate uses GIT to perform incremental content updates using your RESTful backend and then transparently returns control to GIT. In other words, your content *is* a GIT repository, with all the benefits that entails.

*I'm confused. Is Agitate supposed to replace Git?*

NO. Agitate accepts any git command and passes it to git without doing anything, except for the "commit" command. In this case, Agitate first updates your site's content to reflect the content repo via your RESTful backend, and then passes control back to git to perform the commit of your repository.

Usage
-----
