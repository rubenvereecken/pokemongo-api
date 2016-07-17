# Pokemon Go API for Python

This was originally based on
[this API](https://github.com/tejado/pokemongo-api-demo),
you can view this as an advanced
and cleaned up version
based on object-oriented principles.

Additions welcome.

## Demo
`demo.py` includes a demo of the API.

```
➜  python demo.py -a "google" -u "email@gmail.com" -p "thepassword" -l "The Atlantic Ocean"

2016-07-17 16:26:59,947 - INFO - Creating Google session for email@gmail.com
2016-07-17 16:26:59,953 - INFO - Starting new HTTPS connection (1): android.clients.google.com
2016-07-17 16:27:00,362 - INFO - Starting new HTTPS connection (1): android.clients.google.com
2016-07-17 16:27:00,789 - INFO - Location: The Atlantic Ocean
2016-07-17 16:27:00,789 - INFO - Coordinates: 51.01 7.12 0.0
2016-07-17 16:27:00,793 - INFO - Starting new HTTPS connection (1): pgorelease.nianticlabs.com
2016-07-17 16:27:01,633 - INFO - creation_time: 3341800000
team: 3
avatar {
  hair: 1
  shirt: 1
  pants: 1
  hat: 1
  shoes: 1
  eyes: 1
  backpack: 1
}
max_pokemon_storage: 250
max_item_storage: 400
daily_bonus {
  next_defender_bonus_collect_timestamp_ms: 4106877052
}
currency {
  type: "STARDUST"
  quantity: 9001
}
```

This is achieved with minimal coding effort on the client's part
(extract from `demo.py`):

```
  # ... Blabla define the parser
  if args.auth == 'ptc':
      session = api.createPTCSession(args.username, args.password, args.location)
  elif args.auth == 'google':
      session = api.createGoogleSession(args.username, args.password, args.location)

  if session: # do stuff
      profile = session.getProfile()
      logging.info(profile)
```

## Protocol
I also maintain my own version of the
[Pokemon Go Protobuf protocol](https://github.com/rubenvereecken/pokemongo-protocol).
