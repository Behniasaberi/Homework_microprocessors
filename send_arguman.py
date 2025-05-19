import threading

def greet(name):
    print(f"Hello, {name}!")

names = ["Behnia", "Mahdi", "Erfan"]

threads = []
for name in names:
    t = threading.Thread(target=greet, args=(name,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Greeting all done!")
