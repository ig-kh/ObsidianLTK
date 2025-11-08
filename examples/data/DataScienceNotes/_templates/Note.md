---
tags:
date: <% tp.date.now("YYYY-MM-DD") %>
time: <% tp.date.now("HH:mm:ss") %>
location:
layer: bronze
---
<% tp.file.cursor() %>
___
<% tp.file.move("/" + tp.date.now("dddd, MMM Do YYYY") + "@" + tp.date.now("HH") + "'" + tp.date.now("mm") + "'" + tp.date.now("ss")) %>
*Source* [[]]