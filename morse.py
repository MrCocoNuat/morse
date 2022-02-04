from colorama import init #for colors!

import trainer

#colorama supports windows, but not the wordlist loading (yet)
init()

t1 = trainer.Trainer(wpm=30, visual=True)
t2 = trainer.Trainer(wpm=12, farnsworth=True)

while True: #there's just no reason, no reason to exit!
    print("")
    t1.translate()



