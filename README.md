# Api.ai - sample webhook implementation in Python

This is a really simple webhook implementation that gets Api.ai classification JSON (i.e. a JSON output of Api.ai /query endpoint) and returns a fulfillment response.

More info about Api.ai webhooks could be found here:
[Api.ai Webhook](https://docs.api.ai/docs/webhook)

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# What does the service do?

It's an End User License Agreement fulfillment service that uses [ISOM API](https://isom.honeywell.com).
The service takes the 'productname' parameter from the action, and requests EULA from ISOM API.

The service packs the result in the Api.ai webhook-compatible response JSON and returns it to Api.ai.
