# Frequently asked questions


##### Why did you do that? One can use all those libraries independently.

Yes, well. You can, and I did, but I found all of them usable all the time, and built my ecosystem around them.
And installing them all of them, maintaining all the dependencies, and gluing them together in each project using those
helpers is much of a burden. So I just externalized it into a single library.

##### Why Tetra ? Why not use Vue.js/Quasar/Svelte/Angular/React/HTMX?
Sigh. Long story. Because Javascript frontends (while being really cool) more or less are forcing you to code a monolithic frontend facing a plugin-based Django-backend, and to do everything (validation, data management, state) twice: on the frontend in Javascript, *and* on the backend again. Except HTMX, which is cool and different, but more or less forces you to write spaghetti code. There are no components to build upon.

I'd like to allow application plugins to bring their own plugin frontends, which is much easier to achieve using
Django's templating language and Django style components. Conjunto (with Tetra) is trying its best to support component based development.

##### Could you use library XYZ instead of ABC?
Short answer: No.<br/>
Longer answer: Ok, maybe. If it is really better than ABC, try to convince me. Conjunto may not be perfect, but I like it
the way it is.

##### Why are all static files included? This bloats up the library. I want a CDN to serve them!
True. I need Conjunto to serve from "offline" servers in a LAN too. Maybe **you** want to provide a PR to switch between
CDN and locally downloaded libraries, using a setting?