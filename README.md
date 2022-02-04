# morse-code-trainer

A simple utility that helps you train in receiving morse code

`trainer.Trainer` is the main class:

- `__init__(wpm=24, farnsworth=False, visual=False, audio=True)`
initializes a trainer.

  - `wpm`: Words per minute as measured by the `PARIS` standard
  - `farnsworth`: Whether the time between letters/words should be doubled - this will lower effective wpm
  - `visual`: Whether "." and "-" characters should be printed along with the sound
  - `audio`: Whether the speaker should play beeps aloud

- `train()` Receive a random word, type it, and you will see which letters you got right, and which you need to improve on.

- `translate()` translates input you give into morse code

!["assets/screenshot.png"](Screenshot of operation)

Relies on portaudio, you may need to install that.
