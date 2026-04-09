# SS14-Symspeech

This project is a library meant to be used with SS14 Starlight TTS system, it allows for generating audio speech similar to the game Don't Starve, where each character speaks using instrumental sounds. It is not meant to compete with an actual TTS but rather provide an alternative to it.

We use sounds normally used for MIDI playback in SS14, and generate sounds using these instruments.

# How it works
The way it works is - when there is a message sent to the SS14 Starlight-based server, it creates a request in Redis, that is then read by this package, each letter is parsed into a note, applying effects as specified, then converted to OGG file, which is sent back to Redis, the server then reads the value and broadcasts it to the players.

# Sound Settings
Each message can be composed of these values:
```
    id: str - ID of the message.
    t: str - Text of the message.
    r: str - voice ID of the message.
--- Symspeech specific options
    pitch: int - range -24 - 24 - default: 0 - changes the range of the sound, making it sound more or less pitched. it shifts the range higher or lower
    speed: float - range 0.1 - 1.0 - default: 0.44 - Changes the speed of the speech, lower value makes the sounds speak faster, less spacing between letters. Higher is more pause between letters
    pause: float - range 0.05 - 1.0 - default: 0.36 - Changes the pause that is placed in place of spaces as well as punctuation symbols. Higher is more pause.
    poly: int - range 1 - 8 - default: 1 - creates the effect of reverb, makes the speech sound flatter or deeper. More means more reverb.
    scale: int - range 0 - 6 - default: 0 - enum for musical scale used for speech // TODO print scale
    vol: float - range 0.1 - 2.0 - default: 1.0 - volume of the speech. Higher is louder.
    emotion: int - Currently unused.
--- Symspeech specific end
    e: int - range 0 - 6 - additional effects applied to the speech, like radio noise, and such, defined by Starlight, can be expanded. // TODO print effects
    ts: int - timestamp
```
Important to note is, all Symspeech specific options have default values, the SS14 server does not need to send us these values, and the system works just fine, this is useful for testing.

# Voices
Voices available to this Symspeech can be seen in the voices.json file, the voices are also defined in a yaml file on the side of SS14-Starlight based server. Generally its in my opinion better to only remove voices from the list on the side of the SS14 server, the voices technically will be available then to be set via VVWrite, though that should be only available for the admins.

# Installation
This system requires three pieces
1. SS14 Starlight implementation of TTS - This is a required step as most heavy lifting is made by the Starlight server, which handles the communication and playback of TTS.
2. Redis instance - No special config is required here
3. A running instance of SS14-Symspeech.

To connect these pieces together we require a running instance of Redis, both SS14 and Symspeech require Redis url to be provided to them:

## SS14 Config
server_config.toml
```
[tts]
enabled = true
connection_string = "<url>:<port>"
```
the url part is the url to your Redis instance, the port is usually the default Redis port (6379)

### Running in debug
In debug you can still connect to the same Symspeech instance using Redis, you need to find your server_config.toml that is used for debug configuration, probably: `bin/Content.Server/server_config.toml`

## Redis
Any Redis instance would work, personally i recommend running a docker container, even without anything set up for data persistence.

## SS14-Symspeech
config.json
```
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "queue": "tts_jobs"
  }
```
change host and port to be the same as in your SS14 Config.

And thats it. its finished, no more config is needed, even default Starlight voices work without any changes to its code. 
I recommend personally running this config from a docker-compose, for example:

```
  services:                                                                                                                                                                                                                                                                                                        
    redis:
      image: redis:7-alpine                                                                                                                                                                                                                                                                                        
      restart: unless-stopped
      ports:
        - "6379:6379"

    SS14-Symspeech:
      image: fasuh/ss14-symspeech:latest
      restart: unless-stopped
      depends_on:
        - redis
      environment:
        - TTS_REDIS_HOST=redis
        - TTS_REDIS_PORT=6379
        - TTS_MAX_TEXT_LENGTH=50
```

## Running a test
This repository has a script that allows for a preview of the generated voices, how they sound like with various options, all you need to do is to navigate to `/test/test_requests.json` and add your own request that you want to try out, then run `/test_generate.py` and you will see results generated in the folder `/test/output/`
