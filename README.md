# MentalMath

# Getting Started

Create a virtual environment

```
python3 -m venv venv
```

Activate the virtual environment
```
source venv/bin/activate
```

To automatically install everything listed in requirements.txt, just run:

```
pip3 install -r requirements.txt
```

Run the program
```
python3 server.py
```

Access the program
```
http://127.0.0.1:5001
```

# Organization

Backend: Server.py

Data is held in math_data.py and accessed thhrough python functions. 

All templates use base.html and base.css which imports everything automatically. 
