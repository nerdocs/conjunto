# Frequently asked questions


##### Why did you do that? One can use all those libraries independently.

Yes, well. You can, and I did, but I found all of them usable all the time, and built my eco system around them.
And installing them all of them, maintaining all the dependencies, and gluing them togther in each project using those
helpers is much of a burden. So I just externalized it into a single library.

##### Why HTMX? Why not use Vue.js/Quasar/Svelte/Angular/React?
Sigh. Long story. Because these (while being really cool) are forcing you to code a monolithic frontend facing a
plugin-based Django-backend, and to do everything (validation, data management, state) twice: on the frontend *and* on
the backend.
I'd like to allow application plugins to bring their own plugin frontends, which is much easier to achieve using
Django's templating language and HTMX. Conjunto is trying its best to support component based development.
HTMX does not provide that from the start, but in combination with `django-web-components` and some Javascript event
handling this is getting closer.

##### Could you use library XYZ instead of ABC?
Short answer: No.<br/>
Longer answer: Ok, maybe. If it is really better than ABC, try to convince me. Conjunto may not be perfect, but I like it
the way it is.

##### Why are all static files included? This bloats up the library. I want a CDN to serve them!
True. I need Conjunto to serve from "offline" servers in a LAN too. Maybe **you** want to provide a PR to switch between
CDN and locally downloaded libraries, using a setting?