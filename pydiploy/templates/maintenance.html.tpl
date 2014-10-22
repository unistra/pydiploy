<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Maintenance {{ server_name }}</title>

        <style>
            a {
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            body {
                font-family: sans-serif;
                text-align: center;
            }
            h2 {
                color: #333;
                font-size: 3em;
                text-shadow: 0.1em 0.1em 0.1em #aaa;
            }
        </style>
    </head>
    <body>
        <h2>
            {% if maintenance_title %}
            {{ maintenance_title }}
            {% else %}
            {{ server_name }} : system maintenance
            {% endif %}

        </h2>
        <p>
            {% if maintenance_text %}
            {{ maintenance_text }}
            {% else %}
            We apologize for the interruption, but we're currently performing
            maintenance for {{ server_name }} . Please check back again in a few minutes.
            {% endif %}
        </p>
        <p>
        </p>
    </body>
</html>
